"""`PipelineState.create_build_details` refuses a finished stage that did not write its information, and the build
details give only finished stages' information, count the drops and incorrect solves, describe the distilled suites,
and read back the files that they write."""

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId, PipelineStop
from sunnbear._core.benchmark.suites.pipeline.features import FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.selection import CoreComposition, DifficultyClass, SuiteFamily
from sunnbear._core.benchmark.suites.pipeline.state import (
    BenchmarkSuitesBuildDetails,
    CharacterizationResults,
    DistilledSuiteSummary,
    IntervalBounds,
    NearestKeptCandidate,
    PipelineState,
    SuiteMembership,
)
from tests.benchmark.suites.pipeline.example_states import (
    EXAMPLE_DEFINITION,
    build_state_before,
    example_problem_ids,
    example_raw_feature_matrix,
)

_PROBLEM_IDS = [*example_problem_ids(3, formula_number=1), *example_problem_ids(2, formula_number=2)]
_CORE_COMPOSITION = CoreComposition.from_class_counts(dict.fromkeys(DifficultyClass, 64))


def _distilled_state() -> PipelineState:
    """Return a state in which every stage finished: validation rejected 2 candidates, spacing dropped 1, and
    distillation placed the 2 remaining ones in a benchmark suite of 64 and a calibration suite of 64."""
    state = PipelineState()
    accessor = state.create_state_accessor(PipelineStageId.CANDIDATE_GENERATION)
    accessor.add_candidates(dict.fromkeys(_PROBLEM_IDS, IntervalBounds(a=-1.0, b=1.0)))
    state.finish_stage(PipelineStageId.CANDIDATE_GENERATION)
    accessor = state.create_state_accessor(PipelineStageId.CANDIDATE_VALIDATION)
    accessor.reject(_PROBLEM_IDS[0], "bound_to_width_ratio")
    accessor.reject(_PROBLEM_IDS[3], "bisection_count_not_exact")
    accessor.set_c_ranges(dict.fromkeys(accessor.remaining_problem_ids, CRange(c_min=-0.5, c_max=0.5)))
    state.finish_stage(PipelineStageId.CANDIDATE_VALIDATION)
    for stage_id in (PipelineStageId.COARSE_CHARACTERIZATION, PipelineStageId.FULL_CHARACTERIZATION):
        accessor = state.create_state_accessor(stage_id)
        problem_ids = accessor.remaining_problem_ids
        accessor.set_characterization_results(
            CharacterizationResults(
                definition=EXAMPLE_DEFINITION,
                fidelity=FeatureFidelity.COARSE,
                raw_feature_matrix=example_raw_feature_matrix(problem_ids),
                n_incorrect_solves_per_config={problem_id: (idx,) for idx, problem_id in enumerate(problem_ids)},
            )
        )
        if stage_id is PipelineStageId.FULL_CHARACTERIZATION:
            accessor.set_edis(dict.fromkeys(problem_ids, 10.0))
        state.finish_stage(stage_id)
        if stage_id is PipelineStageId.COARSE_CHARACTERIZATION:
            accessor = state.create_state_accessor(PipelineStageId.SPACING)
            accessor.drop(_PROBLEM_IDS[2], "near_duplicate")
            accessor.set_nearest_kept_candidates(
                {_PROBLEM_IDS[2]: NearestKeptCandidate(problem_id=_PROBLEM_IDS[1], distance=0.5)}
            )
            state.finish_stage(PipelineStageId.SPACING)
    accessor = state.create_state_accessor(PipelineStageId.CORE_SELECTION)
    accessor.set_difficulty_classes({_PROBLEM_IDS[1]: DifficultyClass.A, _PROBLEM_IDS[4]: DifficultyClass.B})
    accessor.set_core_composition(_CORE_COMPOSITION)
    state.finish_stage(PipelineStageId.CORE_SELECTION)
    accessor = state.create_state_accessor(PipelineStageId.DISTILLATION)
    accessor.set_suite_memberships(
        {
            _PROBLEM_IDS[1]: SuiteMembership(suite_family=SuiteFamily.BENCHMARK, smallest_containing_suite_size=64),
            _PROBLEM_IDS[4]: SuiteMembership(suite_family=SuiteFamily.CALIBRATION, smallest_containing_suite_size=64),
        }
    )
    accessor.set_distilled_suite_summaries(
        [
            DistilledSuiteSummary(suite_family=SuiteFamily.BENCHMARK, size=64, diversity=0.5),
            DistilledSuiteSummary(suite_family=SuiteFamily.CALIBRATION, size=64, diversity=None),
        ]
    )
    state.finish_stage(PipelineStageId.DISTILLATION)
    return state


@pytest.mark.parametrize("stage_id", list(PipelineStageId))
def test_the_build_details_refuse_a_finished_stage_without_its_information(stage_id: PipelineStageId):
    """A stage that finishes without writing its information makes `create_build_details` raise, naming the stage."""
    # --- arrange ----------------------
    state = build_state_before(stage_id, example_problem_ids(3), core_composition=_CORE_COMPOSITION)
    state.create_state_accessor(stage_id)
    state.finish_stage(stage_id)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=f"did not write their information: .*{stage_id}"):
        state.create_build_details()


def test_the_build_details_hold_only_the_information_of_finished_stages():
    """Core selection stored the classes, then stopped the run, so the build details hold the stop, the information of
    the stages before core selection, and none of core selection's."""
    # --- arrange ----------------------
    problem_ids = example_problem_ids(3)
    state = build_state_before(PipelineStageId.CORE_SELECTION, problem_ids)
    state.create_state_accessor(PipelineStageId.CORE_SELECTION).set_difficulty_classes(
        dict.fromkeys(problem_ids, DifficultyClass.A)
    )
    stop = PipelineStop(stage_id=PipelineStageId.CORE_SELECTION, reason="too few candidates")

    # --- act --------------------------
    build_details = state.create_build_details(stop=stop)

    # --- assert -----------------------
    assert build_details.stop == stop
    assert build_details.finished_stage_ids == tuple(PipelineStageId)[:5]
    assert build_details.edis() == dict.fromkeys(problem_ids, 10.0)
    assert build_details.difficulty_classes() is None
    assert build_details.suite_compositions() is None
    assert build_details.incorrect_solves_per_config(PipelineStageId.COARSE_CHARACTERIZATION) is not None


def test_the_build_details_count_the_drops_per_formula_stage_and_reason():
    """The drop counts hold validation's 2 rejections and spacing's drop, in run order; validation received 3 and 2
    candidates of the 2 formulas and kept 2 and 1, and spacing received 2 and 1 and kept 1 and 1."""
    # --- act --------------------------
    build_details = _distilled_state().create_build_details()

    # --- assert -----------------------
    assert build_details.drop_counts().rows() == [
        ("f99.1", PipelineStageId.CANDIDATE_VALIDATION.value, "bound_to_width_ratio", True, 1),
        ("f99.2", PipelineStageId.CANDIDATE_VALIDATION.value, "bisection_count_not_exact", True, 1),
        ("f99.1", PipelineStageId.SPACING.value, "near_duplicate", False, 1),
    ]
    assert build_details.candidate_counts(PipelineStageId.CANDIDATE_VALIDATION).rows() == [
        ("f99.1", 3, 2),
        ("f99.2", 2, 1),
    ]
    assert build_details.candidate_counts(PipelineStageId.SPACING).rows() == [("f99.1", 2, 1), ("f99.2", 1, 1)]
    assert build_details.remaining_problem_ids == (_PROBLEM_IDS[1], _PROBLEM_IDS[4])


def test_the_build_details_count_each_configs_incorrect_solves():
    """Over the 3 candidates that coarse characterization kept, with 0, 1 and 2 incorrect solves of 32 each, the
    config has 3 incorrect solves of 96."""
    # --- act --------------------------
    table = (
        _distilled_state().create_build_details().incorrect_solves_per_config(PipelineStageId.COARSE_CHARACTERIZATION)
    )

    # --- assert -----------------------
    assert table.rows() == [("bisection", 96, 3, 3 / 96)]


def test_the_build_details_describe_each_distilled_suite():
    """Each suite's row gives its family, size, count per class and diversity score."""
    # --- act --------------------------
    table = _distilled_state().create_build_details().suite_compositions()

    # --- assert -----------------------
    assert table.select("suite_family", "size", "n_candidates_a", "n_candidates_b", "diversity").rows() == [
        ("benchmark", 64, 1, 0, 0.5),
        ("calibration", 64, 0, 1, None),
    ]


def test_the_build_details_read_back_the_files_that_they_write(tmp_path):
    """Every read method of the build details read back from their files gives what it gives on the run's own."""
    # --- arrange ----------------------
    build_details = _distilled_state().create_build_details(
        stop=PipelineStop(stage_id=PipelineStageId.DISTILLATION, reason="example")
    )

    # --- act --------------------------
    build_details.write_files(tmp_path / "build_details")
    read_back = BenchmarkSuitesBuildDetails.read_files(tmp_path / "build_details")

    # --- assert -----------------------
    assert (read_back.finished_stage_ids, read_back.stop) == (build_details.finished_stage_ids, build_details.stop)
    assert read_back.problem_ids == build_details.problem_ids
    assert [read_back.drop_of(p) for p in _PROBLEM_IDS] == [build_details.drop_of(p) for p in _PROBLEM_IDS]
    for read_method in [
        "interval_bounds",
        "c_ranges",
        "nearest_kept_candidates",
        "edis",
        "difficulty_classes",
        "core_composition",
        "suite_memberships",
        "distilled_suite_summaries",
    ]:
        assert getattr(read_back, read_method)() == getattr(build_details, read_method)()
    for stage_id in (PipelineStageId.COARSE_CHARACTERIZATION, PipelineStageId.FULL_CHARACTERIZATION):
        results, read_back_results = (
            details.characterization_results(stage_id) for details in (build_details, read_back)
        )
        assert (read_back_results.definition, read_back_results.fidelity) == (results.definition, results.fidelity)
        assert read_back_results.raw_feature_matrix.problem_ids == results.raw_feature_matrix.problem_ids
        np.testing.assert_array_equal(read_back_results.raw_feature_matrix.values, results.raw_feature_matrix.values)
        assert read_back_results.n_incorrect_solves_per_config == results.n_incorrect_solves_per_config


@pytest.mark.parametrize("n_finished_stages", [0, 3])
def test_the_build_details_of_a_run_that_stopped_early_read_back_their_files(tmp_path, n_finished_stages: int):
    """The build details of a run in which no stage, or only the first 3 stages, finished have no files for the
    later stages, so the ones read back hold none of the later stages' information either."""
    # --- arrange ----------------------
    stage_id = list(PipelineStageId)[n_finished_stages]
    build_details = build_state_before(stage_id, example_problem_ids(3)).create_build_details()

    # --- act --------------------------
    build_details.write_files(tmp_path)
    read_back = BenchmarkSuitesBuildDetails.read_files(tmp_path)

    # --- assert -----------------------
    assert read_back.finished_stage_ids == tuple(PipelineStageId)[:n_finished_stages]
    assert read_back.c_ranges() == build_details.c_ranges()
    assert read_back.nearest_kept_candidates() is None
    assert read_back.core_composition() is None
    assert read_back.incorrect_solves_per_config(PipelineStageId.FULL_CHARACTERIZATION) is None
