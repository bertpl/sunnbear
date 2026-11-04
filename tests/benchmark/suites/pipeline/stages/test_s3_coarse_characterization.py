"""`CoarseCharacterizationStage` stores the raw features, the block scales and the incorrect solves of the kept
candidates, rejects the others, and gives the same results with 1 or 2 workers."""

import math

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
)
from sunnbear._core.benchmark.suites.pipeline.state import (
    CharacterizationResults,
    CoarseCharacterizationStateAccessor,
    PipelineState,
)
from sunnbear._core.problems.core import FormulaRegistry, ProblemId
from sunnbear._core.solvers.core import SolverConfigRegistry
from sunnbear._core.utils.module_imports import worker_pool_for_modules
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls
from tests.benchmark.suites.pipeline.example_states import build_state_before, record_calls


def _core_solver_configs():
    """Return the built-in solver configs whose role marks them for characterizing test problems."""
    return [config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization]


def _characterize(
    stage: CoarseCharacterizationStage, problem_ids: list[str], monkeypatch: pytest.MonkeyPatch
) -> tuple[PipelineState, CharacterizationResults]:
    """Run `stage` on the candidates `problem_ids`, each with the c-range ``[-0.5, 0.5]``, and return its results."""
    state = build_state_before(
        PipelineStageId.COARSE_CHARACTERIZATION,
        [ProblemId.from_string(problem_id) for problem_id in problem_ids],
        c_range=CRange(c_min=-0.5, c_max=0.5),
    )
    calls = record_calls(monkeypatch, CoarseCharacterizationStateAccessor, "set_characterization_results")
    state.run_stage(stage, worker_pool=WorkerPool(n_workers=1))
    [(results,)] = calls
    return state, results


def test_the_stage_stores_the_kept_candidates_features_and_rejects_the_others(isolated_formula_registry, monkeypatch):
    """The candidate with a simple root gets 25 raw features and no scales, because as the only kept candidate it
    leaves no pair to measure; the candidate whose f is NaN around its root is rejected."""
    # --- arrange ----------------------
    define_formula_cls((99, 971), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    define_formula_cls((99, 972), lambda x, c: math.nan if abs(x - c - 1 / 3) < 0.1 else x - c - 1 / 3, -1.0, 1.0)
    stage = CoarseCharacterizationStage(_core_solver_configs())

    # --- act --------------------------
    state, results = _characterize(stage, ["f99.971", "f99.972"], monkeypatch)

    # --- assert -----------------------
    assert len(stage.definition.feature_names) == 25
    assert (results.definition, results.fidelity) == (stage.definition, FeatureFidelity.COARSE)
    assert results.raw_feature_matrix.problem_ids == (ProblemId.from_string("f99.971"),)
    assert results.raw_feature_matrix.values.shape == (1, 25)
    assert results.block_scales is None
    drop = state.drop_of(ProblemId.from_string("f99.972"))
    assert (drop.stage_id, drop.reason, drop.is_rejection) == (stage.stage_id, "function_error", True)


def test_the_stage_stores_each_configs_incorrect_solves_per_candidate(isolated_formula_registry, monkeypatch):
    """The test runs 2 candidates: a simple root, and (x - c - 1/3)^21, whose flat root makes every Illinois solve
    incorrect and every other core config's solve correct; the 2 candidates have scales."""
    # --- arrange ----------------------
    define_formula_cls((99, 973), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    define_formula_cls((99, 974), lambda x, c: (x - c - 1 / 3) ** 21, -1.0, 1.0)
    stage = CoarseCharacterizationStage(_core_solver_configs())

    # --- act --------------------------
    _, results = _characterize(stage, ["f99.973", "f99.974"], monkeypatch)

    # --- assert -----------------------
    n_solves = FeatureFidelity.COARSE.solver_mc_size
    assert results.n_incorrect_solves_per_config == {
        ProblemId.from_string("f99.973"): (0,) * len(stage.definition.solver_ids),
        ProblemId.from_string("f99.974"): tuple(
            n_solves if solver_id == "illinois" else 0 for solver_id in stage.definition.solver_ids
        ),
    }
    assert all(scale > 0.0 for scale in results.block_scales.scale_per_block.values())


@pytest.mark.only_with_numba_jit
def test_the_stage_gives_the_same_results_with_1_or_2_workers():
    """With 2 worker processes, the raw features equal those of a run in this process, on 3 valid shipped candidates
    of 2 formulas."""
    # --- arrange ----------------------
    formulas = [formula for formula in FormulaRegistry.formulas() if formula.number in {(1, 4, 2, 2), (1, 4, 2, 4)}]
    core_solver_configs = _core_solver_configs()
    module_names = {type(formula).__module__ for formula in formulas} | {
        config.declaring_module_name for config in core_solver_configs
    }

    # --- act --------------------------
    spacing_accessors = []
    for n_workers in (1, 2):
        with worker_pool_for_modules(n_workers=n_workers, module_names=module_names) as worker_pool:
            state = PipelineState()
            for stage in [
                CandidateGenerationStage(formulas),
                CandidateValidationStage(),
                CoarseCharacterizationStage(core_solver_configs),
            ]:
                state.run_stage(stage, worker_pool=worker_pool)
        spacing_accessors.append(state.create_state_accessor(PipelineStageId.SPACING))

    # --- assert -----------------------
    in_process_matrix, worker_processes_matrix = (
        accessor.coarse_scaled_feature_matrix() for accessor in spacing_accessors
    )
    assert len(in_process_matrix.problem_ids) == 3
    assert worker_processes_matrix.problem_ids == in_process_matrix.problem_ids
    np.testing.assert_array_equal(worker_processes_matrix.values, in_process_matrix.values)


def test_the_stage_needs_a_core_solver_config():
    """A characterization stage without core solver configs has no solvers block, so it refuses to be created."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="at least 1 core solver config"):
        CoarseCharacterizationStage([])
