"""This module builds pipeline states on synthetic information, so that a test of 1 stage needs no earlier stage's work.

`build_state_before` runs the state accessors of every stage before a given stage, writes example information through
them, and returns the state, which then creates the given stage's accessor. `record_calls` records the information
that a stage writes through 1 method of its accessor.
"""

from collections import Counter
from collections.abc import Mapping, Sequence

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, CRange, max_fevals_for
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import (
    SNUFFLED_PROPERTIES,
    FeatureFidelity,
    FeatureMatrix,
    DiversityFeatureFactory,
)
from sunnbear._core.benchmark.suites.pipeline.selection import CoreComposition, DifficultyClass
from sunnbear._core.benchmark.suites.pipeline.state import CharacterizationResults, IntervalBounds, PipelineState
from sunnbear._core.problems.core import ProblemId

# The example states characterize the candidates with 1 core solver config, which gives 20 features.
EXAMPLE_DEFINITION = DiversityFeatureFactory(solver_ids=("bisection",))
_MAX_FEVALS = max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)
_DEFAULT_C_RANGE = CRange(c_min=-1.0, c_max=1.0)


def example_problem_ids(n_candidates: int, *, formula_number: int = 1) -> list[ProblemId]:
    """Return the ids of `n_candidates` candidates of the formula numbered ``(99, formula_number)``."""
    return [ProblemId.from_string(f"f99.{formula_number}[p={idx + 1}]") for idx in range(n_candidates)]


def example_raw_feature_matrix(problem_ids: Sequence[ProblemId], *, seed: int = 3) -> FeatureMatrix:
    """Return random raw features of `problem_ids`, with evaluation counts in [2, max_fevals] in the solvers block."""
    rng = np.random.default_rng(seed=seed)
    n_solvers_features = len(EXAMPLE_DEFINITION.feature_names) - len(SNUFFLED_PROPERTIES)
    values = np.hstack(
        [
            rng.uniform(2, _MAX_FEVALS, size=(len(problem_ids), n_solvers_features)),
            rng.random((len(problem_ids), len(SNUFFLED_PROPERTIES))),
        ]
    )
    return FeatureMatrix(problem_ids=tuple(problem_ids), values=values)


def example_characterization_results(raw_feature_matrix: FeatureMatrix) -> CharacterizationResults:
    """Return the results of a characterization at the coarse fidelity that keeps every candidate of the matrix."""
    return CharacterizationResults(
        definition=EXAMPLE_DEFINITION,
        fidelity=FeatureFidelity.COARSE,
        raw_feature_matrix=raw_feature_matrix,
        block_scales=EXAMPLE_DEFINITION.fit_block_scales(raw_feature_matrix),
        n_incorrect_solves=dict.fromkeys(raw_feature_matrix.problem_ids, (0,)),
    )


def build_state_before(
    stage_id: PipelineStageId,
    problem_ids: Sequence[ProblemId],
    *,
    coarse_raw_feature_matrix: FeatureMatrix | None = None,
    edis: Mapping[ProblemId, float] | None = None,
    c_range: CRange = _DEFAULT_C_RANGE,
    core_composition: CoreComposition | None = None,
) -> PipelineState:
    """Return a state in which every stage before `stage_id` has run on `problem_ids` and kept them all.

    The stages write this example information:

    - generation and validation: the interval ``[-1, 1]`` and the c-range `c_range` of each candidate;
    - each characterization: the raw features `coarse_raw_feature_matrix`, by default those of
      `example_raw_feature_matrix`, with their block scales and no incorrect solve;
    - full characterization: the EDIs `edis`, by default 10 for each candidate;
    - core selection: each candidate's class from its EDI, and `core_composition`, by default the composition of the
      largest Core that the classes fill.
    """
    state = PipelineState()
    raw_feature_matrix = coarse_raw_feature_matrix or example_raw_feature_matrix(problem_ids)
    edis = edis if edis is not None else dict.fromkeys(problem_ids, 10.0)
    for earlier_stage_id in list(PipelineStageId)[: list(PipelineStageId).index(stage_id)]:
        accessor = state.create_accessor(earlier_stage_id)
        match earlier_stage_id:
            case PipelineStageId.CANDIDATE_GENERATION:
                accessor.add_candidates(dict.fromkeys(problem_ids, IntervalBounds(a=-1.0, b=1.0)))
            case PipelineStageId.CANDIDATE_VALIDATION:
                accessor.set_c_ranges(dict.fromkeys(problem_ids, c_range))
            case PipelineStageId.COARSE_CHARACTERIZATION:
                accessor.set_characterization_results(example_characterization_results(raw_feature_matrix))
            case PipelineStageId.SPACING:
                accessor.set_nearest_kept_candidates({})
            case PipelineStageId.FULL_CHARACTERIZATION:
                accessor.set_characterization_results(example_characterization_results(raw_feature_matrix))
                accessor.set_edis(edis)
            case PipelineStageId.CORE_SELECTION:
                difficulty_classes = {
                    problem_id: DifficultyClass.from_edi(edi, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)
                    for problem_id, edi in edis.items()
                }
                accessor.set_difficulty_classes(difficulty_classes)
                accessor.set_core_composition(
                    core_composition or CoreComposition.from_class_counts(Counter(difficulty_classes.values()))
                )
        state.finish_stage(earlier_stage_id)
    return state


def record_calls(monkeypatch: pytest.MonkeyPatch, accessor_cls: type, method_name: str) -> list[tuple]:
    """Return a list that collects the arguments of each call to the method `method_name` of `accessor_cls`.

    The method still runs, so the state receives the information as it does without the recording.
    """
    calls: list[tuple] = []
    method = getattr(accessor_cls, method_name)

    def recording_method(self: object, *args: object) -> None:
        """Record the arguments of the call, then make the call."""
        calls.append(args)
        method(self, *args)

    monkeypatch.setattr(accessor_cls, method_name, recording_method)
    return calls
