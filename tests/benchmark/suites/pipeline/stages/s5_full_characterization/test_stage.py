"""`FullCharacterizationStage` stores the full raw features, their block scales and each kept candidate's EDI."""

import numpy as np
import pytest

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import EDI_GPQ_LEVEL, SOLVERS_GPQ_LEVELS, FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.stages import FullCharacterizationStage
from sunnbear._core.benchmark.suites.pipeline.state import FullCharacterizationStateAccessor
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.solvers.core import SolverConfigRegistry
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls
from tests.benchmark.suites.pipeline.example_states import build_state_before, record_calls


@pytest.mark.only_with_numba_jit
def test_the_stage_stores_the_full_features_their_scales_and_the_edis(isolated_formula_registry, monkeypatch):
    """On 2 candidates with a simple root, the stage stores their raw features at the full fidelity, a positive scale
    per block, and each candidate's EDI, which equals its gpq at the EDI's level."""
    # --- arrange ----------------------
    define_formula_cls((99, 981), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    define_formula_cls((99, 982), lambda x, c: (x - c - 1 / 3) ** 3 + 0.1 * (x - c - 1 / 3), -1.0, 1.0)
    problem_ids = [ProblemId.from_string(problem_id) for problem_id in ["f99.981", "f99.982"]]
    state = build_state_before(
        PipelineStageId.FULL_CHARACTERIZATION, problem_ids, c_range=CRange(c_min=-0.5, c_max=0.5)
    )
    core_solver_configs = [
        config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization
    ]
    stage = FullCharacterizationStage(core_solver_configs)
    results_calls = record_calls(monkeypatch, FullCharacterizationStateAccessor, "set_characterization_results")
    edis_calls = record_calls(monkeypatch, FullCharacterizationStateAccessor, "set_edis")

    # --- act --------------------------
    stage.run(state.create_state_accessor(stage.stage_id), worker_pool=WorkerPool(n_workers=1))

    # --- assert -----------------------
    [(results,)], [(edis,)] = results_calls, edis_calls
    assert results.fidelity is FeatureFidelity.FULL
    assert results.raw_feature_matrix.problem_ids == tuple(problem_ids)
    assert all(scale > 0.0 for scale in results.block_scales.scale_per_block.values())
    edi_column = len(stage.definition.solver_ids) + SOLVERS_GPQ_LEVELS.index(EDI_GPQ_LEVEL)
    np.testing.assert_allclose(
        [edis[problem_id] for problem_id in problem_ids], results.raw_feature_matrix.values[:, edi_column]
    )
