"""`CoarseCharacterizationStage` adds the coarse feature vector of each kept candidate and the scale of each feature
block, reports the rejected candidates, and gives the same output with 1 or 2 workers."""

import math

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import (
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    RejectionReason,
)
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
)
from sunnbear._core.problems.core import FormulaRegistry
from sunnbear._core.solvers.core import SolverConfigRegistry
from sunnbear._core.utils.module_imports import worker_pool_for_modules
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


def _core_solver_configs():
    """Return the built-in solver configs whose role marks them for characterizing test problems."""
    return [config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization]


def test_the_stage_adds_the_features_of_the_kept_candidates_and_reports_the_others(isolated_formula_registry):
    """The candidate with a simple root gets 25 features and null scales, because as the only kept candidate it leaves
    no pair to measure; the candidate whose f is NaN around its root is rejected."""
    # --- arrange ----------------------
    define_formula_cls((99, 971), lambda x, c: x - c - 1 / 3, -1.0, 1.0)
    define_formula_cls((99, 972), lambda x, c: math.nan if abs(x - c - 1 / 3) < 0.1 else x - c - 1 / 3, -1.0, 1.0)
    previous_table = pl.DataFrame(
        {
            "problem_id": ["f99.971", "f99.972"],
            "a": [-1.0, -1.0],
            "b": [1.0, 1.0],
            "c_min": [-0.5, -0.5],
            "c_max": [0.5, 0.5],
        }
    )
    stage = CoarseCharacterizationStage(_core_solver_configs())

    # --- act --------------------------
    output = stage.compute_output(previous_table, worker_pool=WorkerPool(n_workers=1))

    # --- assert -----------------------
    column_names = stage.feature_column_names
    scale_column_names = stage.feature_scale_column_names()
    assert len(column_names) == 25
    assert output.table.columns == [*previous_table.columns, *column_names, *scale_column_names]
    assert output.table["problem_id"].to_list() == ["f99.971"]
    assert all(0.0 <= value <= 1.0 for value in output.table.select(column_names).row(0))
    assert output.table.select(scale_column_names).row(0) == (None, None)
    rejected_candidates = output.reports[REJECTED_CANDIDATES_REPORT_NAME]
    assert rejected_candidates.schema == pl.Schema({**previous_table.schema, **REJECTED_BY_SCHEMA})
    assert rejected_candidates.rows() == [("f99.972", -1.0, 1.0, -0.5, 0.5, RejectionReason.FUNCTION_ERROR.value)]


@pytest.mark.only_with_numba_jit
def test_the_stage_gives_the_same_output_with_1_or_2_workers():
    """With 2 worker processes, the output equals that of a run in this process, on 3 valid shipped candidates of 2
    formulas."""
    # --- arrange ----------------------
    formulas = [formula for formula in FormulaRegistry.formulas() if formula.number in {(1, 4, 2, 2), (1, 4, 2, 4)}]
    in_process = WorkerPool(n_workers=1)
    candidates = CandidateGenerationStage(formulas).compute_output(pl.DataFrame(), worker_pool=in_process)
    valid_candidates = CandidateValidationStage().compute_output(candidates.table, worker_pool=in_process).table
    core_solver_configs = _core_solver_configs()
    module_names = {type(formula).__module__ for formula in formulas} | {
        config.declaring_module_name for config in core_solver_configs
    }

    # --- act --------------------------
    in_process_output = CoarseCharacterizationStage(core_solver_configs).compute_output(
        valid_candidates, worker_pool=in_process
    )
    with worker_pool_for_modules(n_workers=2, module_names=module_names) as worker_pool:
        worker_processes_output = CoarseCharacterizationStage(core_solver_configs).compute_output(
            valid_candidates, worker_pool=worker_pool
        )

    # --- assert -----------------------
    assert in_process_output.table.height == 3
    assert worker_processes_output.table.equals(in_process_output.table)
    for report_name, report in worker_processes_output.reports.items():
        assert report.equals(in_process_output.reports[report_name])


def test_the_stage_needs_a_core_solver_config():
    """A characterization stage without core solver configs has no solvers block, so it refuses to be created."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="at least 1 core solver config"):
        CoarseCharacterizationStage([])
