"""The state accessors give a stage only the candidates that no stage has dropped, write each piece of a stage's
information once and only when it covers exactly the remaining candidates, and give the candidate pool only once the
pool can be built."""

from collections.abc import Callable

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, CRange
from sunnbear._core.benchmark.suites.benchmark_suite import BenchmarkSuite
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import DiversityFeatureFactory
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyTier
from sunnbear._core.benchmark.suites.pipeline.state import (
    IntervalBounds,
    NearestKeptCandidate,
    PipelineStateAccessor,
    SuiteSelectionDetails,
)
from tests.benchmark.suites.pipeline.example_states import (
    build_state_before,
    example_characterization_results,
    example_problem_ids,
    example_raw_feature_matrix,
)

_PROBLEM_IDS = example_problem_ids(3)
_C_RANGE = CRange(c_min=-1.0, c_max=1.0)


def _accessor(stage_id: PipelineStageId) -> PipelineStateAccessor:
    """Return the accessor of `stage_id` on a state in which every earlier stage kept the 3 example candidates."""
    return build_state_before(stage_id, _PROBLEM_IDS).create_state_accessor(stage_id)


def _selection_details(series_id: str, name: str, problem_ids: list) -> SuiteSelectionDetails:
    """Return the selection details of a suite of `problem_ids` that no max-div run selected, with no quotas."""
    return SuiteSelectionDetails(
        benchmark_suite=BenchmarkSuite(series_id=series_id, name=name, aliases=(), problem_ids=tuple(problem_ids)),
        quota_fulfillments=(),
        diversity=1.0,
    )


# Each entry is an accessor method that stores information on every remaining candidate, with the stage whose
# accessor has the method.
_WRITES_OF_EACH_CANDIDATE: dict[str, tuple[PipelineStageId, Callable[[PipelineStateAccessor, list], None]]] = {
    "c_ranges": (
        PipelineStageId.CANDIDATE_VALIDATION,
        lambda accessor, problem_ids: accessor.set_c_ranges(dict.fromkeys(problem_ids, _C_RANGE)),
    ),
    "characterization_results": (
        PipelineStageId.COARSE_CHARACTERIZATION,
        lambda accessor, problem_ids: accessor.set_characterization_results(
            example_characterization_results(example_raw_feature_matrix(problem_ids))
        ),
    ),
    "difficulty_tiers": (
        PipelineStageId.SUITE_SELECTION,
        lambda accessor, problem_ids: accessor.set_difficulty_tiers(dict.fromkeys(problem_ids, DifficultyTier.A)),
    ),
    "suite_selection_details": (
        PipelineStageId.SUITE_SELECTION,
        lambda accessor, problem_ids: accessor.set_suite_selection_details(
            [
                _selection_details("sb-a", "sb-2a", problem_ids[:2]),
                _selection_details("sb-b", "sb-1b", problem_ids[2:]),
            ]
        ),
    ),
}

# Each entry is an accessor method that registers the candidates or stores information that is not kept per
# candidate, with the stage whose accessor has the method.
_OTHER_WRITES: dict[str, tuple[PipelineStageId, Callable[[PipelineStateAccessor, list], None]]] = {
    "candidates": (
        PipelineStageId.CANDIDATE_GENERATION,
        lambda accessor, problem_ids: accessor.add_candidates(
            dict.fromkeys(problem_ids, IntervalBounds(a=-1.0, b=1.0))
        ),
    ),
    "spacing_min_distance": (
        PipelineStageId.SPACING,
        lambda accessor, problem_ids: accessor.set_spacing_min_distance(0.1),
    ),
}


@pytest.mark.parametrize("write_name", list(_WRITES_OF_EACH_CANDIDATE))
def test_a_write_covers_exactly_the_remaining_candidates(write_name: str):
    """Information that misses 1 remaining candidate is refused; information on every remaining candidate is stored."""
    # --- arrange ----------------------
    stage_id, write = _WRITES_OF_EACH_CANDIDATE[write_name]
    accessor = _accessor(stage_id)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="takes information on 3 candidates: 0 other candidates given, 1 missing"):
        write(accessor, _PROBLEM_IDS[:2])
    write(accessor, _PROBLEM_IDS)


@pytest.mark.parametrize("write_name", [*_WRITES_OF_EACH_CANDIDATE, *_OTHER_WRITES])
def test_each_piece_of_information_is_written_once(write_name: str):
    """An accessor method refuses to write the same piece of information a second time."""
    # --- arrange ----------------------
    stage_id, write = {**_WRITES_OF_EACH_CANDIDATE, **_OTHER_WRITES}[write_name]
    accessor = _accessor(stage_id)
    write(accessor, _PROBLEM_IDS)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="writes each piece of its stage's information once"):
        write(accessor, _PROBLEM_IDS)


def test_an_accessor_gives_and_takes_only_the_remaining_candidates():
    """After validation rejects 1 candidate, its accessor gives the bounds of the other 2 only, refuses to reject the
    candidate again, and coarse characterization's accessor gives the c-ranges of the other 2 only."""
    # --- arrange ----------------------
    state = build_state_before(PipelineStageId.CANDIDATE_VALIDATION, _PROBLEM_IDS)
    accessor = state.create_state_accessor(PipelineStageId.CANDIDATE_VALIDATION)

    # --- act --------------------------
    accessor.reject(_PROBLEM_IDS[0], "bound_to_width_ratio")
    accessor.set_c_ranges(dict.fromkeys(_PROBLEM_IDS[1:], _C_RANGE))
    state.finish_stage(PipelineStageId.CANDIDATE_VALIDATION)

    # --- assert -----------------------
    assert list(accessor.interval_bounds()) == _PROBLEM_IDS[1:]
    with pytest.raises(ValueError, match="dropped already"):
        accessor.reject(_PROBLEM_IDS[0], "bound_to_width_ratio")
    assert list(state.create_state_accessor(PipelineStageId.COARSE_CHARACTERIZATION).c_ranges()) == _PROBLEM_IDS[1:]


def test_spacing_takes_the_nearest_kept_candidates_of_its_own_drops_only():
    """Spacing's accessor gives the scaled coarse features of the remaining candidates, and refuses a nearest kept
    candidate for a candidate that it did not drop."""
    # --- arrange ----------------------
    accessor = _accessor(PipelineStageId.SPACING)
    raw_feature_matrix = example_raw_feature_matrix(_PROBLEM_IDS)
    nearest_kept_candidate = NearestKeptCandidate(problem_id=_PROBLEM_IDS[0], distance=0.0)

    # --- act --------------------------
    accessor.drop(_PROBLEM_IDS[1], "near_duplicate")
    scaled_feature_matrix = accessor.coarse_scaled_feature_matrix()

    # --- assert -----------------------
    factory = DiversityFeatureFactory()
    expected_matrix = factory.build_scaled_matrix(
        raw_feature_matrix.subset([_PROBLEM_IDS[0], _PROBLEM_IDS[2]]), factory.fit_block_scales(raw_feature_matrix)
    )
    assert scaled_feature_matrix.problem_ids == expected_matrix.problem_ids
    np.testing.assert_array_equal(scaled_feature_matrix.values, expected_matrix.values)
    with pytest.raises(ValueError, match="takes information on 1 candidates: 1 other candidates given, 1 missing"):
        accessor.set_nearest_kept_candidates({_PROBLEM_IDS[2]: nearest_kept_candidate})
    accessor.set_nearest_kept_candidates({_PROBLEM_IDS[1]: nearest_kept_candidate})


def test_spacing_gets_the_coarse_edis_of_the_remaining_candidates():
    """After spacing dropped 1 of 3 candidates, its accessor gives coarse characterization's EDIs of the other 2."""
    # --- arrange ----------------------
    edis = dict(zip(_PROBLEM_IDS, [30.0, 10.0, 20.0], strict=True))
    accessor = build_state_before(PipelineStageId.SPACING, _PROBLEM_IDS, edis=edis).create_state_accessor(
        PipelineStageId.SPACING
    )

    # --- act --------------------------
    accessor.drop(_PROBLEM_IDS[1], "near_duplicate")

    # --- assert -----------------------
    assert accessor.coarse_edis() == {_PROBLEM_IDS[0]: 30.0, _PROBLEM_IDS[2]: 20.0}


def test_spacing_has_no_scaled_features_without_scales():
    """After coarse characterization kept 1 candidate only, it has no scales, so spacing's accessor gives no matrix."""
    # --- act / assert -----------------
    assert (
        build_state_before(PipelineStageId.SPACING, _PROBLEM_IDS[:1])
        .create_state_accessor(PipelineStageId.SPACING)
        .coarse_scaled_feature_matrix()
        is None
    )


def test_the_candidate_pool_pairs_each_candidate_with_its_features_edi_and_tier():
    """Suite selection's pool holds each candidate's scaled features and EDI from fine characterization, and the tier of
    that EDI for `DEFAULT_N_BISECTION_FEVALS`, in the order of candidate generation."""
    # --- arrange ----------------------
    edis = dict(zip(_PROBLEM_IDS, [5.0, 30.0, 15.0], strict=True))
    accessor = build_state_before(PipelineStageId.SUITE_SELECTION, _PROBLEM_IDS, edis=edis).create_state_accessor(
        PipelineStageId.SUITE_SELECTION
    )

    # --- act --------------------------
    candidate_pool = accessor.candidate_pool()

    # --- assert -----------------------
    assert candidate_pool.feature_matrix.problem_ids == tuple(_PROBLEM_IDS)
    np.testing.assert_array_equal(candidate_pool.edis, list(edis.values()))
    assert candidate_pool.n_bisection_fevals == DEFAULT_N_BISECTION_FEVALS
    assert list(candidate_pool.difficulty_tiers.values()) == [DifficultyTier.A, DifficultyTier.C, DifficultyTier.B]


def test_the_candidate_pool_needs_the_scales():
    """Suite selection's accessor gives no pool after fine characterization kept 1 candidate only, which leaves fine
    characterization without scales."""
    # --- arrange ----------------------
    accessor_without_scales = build_state_before(
        PipelineStageId.SUITE_SELECTION, _PROBLEM_IDS[:1]
    ).create_state_accessor(PipelineStageId.SUITE_SELECTION)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="needs the scales of fine characterization"):
        accessor_without_scales.candidate_pool()
