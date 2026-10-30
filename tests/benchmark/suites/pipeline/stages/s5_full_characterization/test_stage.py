"""`FullCharacterizationStage` adds the full feature vector of each kept candidate and the scale of each block."""

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.stages import FullCharacterizationStage
from sunnbear._core.solvers.core import SolverConfigRegistry
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


@pytest.mark.only_with_numba_jit
def test_the_stage_adds_the_full_features_and_their_scales(isolated_formula_registry):
    """On 2 candidates with a simple root, the stage adds the full features, each in [0, 1], and
    a positive scale per block."""
    # --- arrange ----------------------
    define_formula_cls((99, 981), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    define_formula_cls((99, 982), lambda x, c: (x - c - 1 / 3) ** 3 + 0.1 * (x - c - 1 / 3), -1.0, 1.0)
    previous_table = pl.DataFrame(
        {
            "problem_id": ["f99.981", "f99.982"],
            "a": [-1.0, -1.0],
            "b": [1.0, 1.0],
            "c_min": [-0.5, -0.5],
            "c_max": [0.5, 0.5],
        }
    )
    core_solver_configs = [
        config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization
    ]
    stage = FullCharacterizationStage(core_solver_configs)

    # --- act --------------------------
    output = stage.compute_output(previous_table, worker_pool=WorkerPool(n_workers=1))

    # --- assert -----------------------
    column_names = stage.feature_column_names
    scale_column_names = stage.feature_scale_column_names()
    assert all(column_name.startswith("full_") for column_name in [*column_names, *scale_column_names])
    assert output.table.columns == [*previous_table.columns, *column_names, *scale_column_names]
    assert all(0.0 <= value <= 1.0 for row in output.table.select(column_names).rows() for value in row)
    assert all(scale > 0.0 for scale in output.table.select(scale_column_names).row(0))
