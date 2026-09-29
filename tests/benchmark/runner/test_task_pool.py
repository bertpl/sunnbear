"""`BenchmarkTaskPool` runs tasks in worker processes that import the run's solver config modules."""

import sys
import types

import pytest

import sunnbear.functions as functions  # Import the module, so pytest does not try to collect `TestFunction`.
from sunnbear._core.benchmark.runner.run_settings import BenchmarkRunSettings
from sunnbear._core.benchmark.runner.task import BenchmarkTask
from sunnbear._core.benchmark.runner.task_pool import BenchmarkTaskPool
from sunnbear.solvers import SolverConfigRegistry

_SAMPLE_SOLVER_CONFIG_MODULE_NAME = f"{__name__.rpartition('.')[0]}.sample_solver_config"


@pytest.mark.usefixtures("isolated_solver_config_registry")
def test_workers_import_the_module_that_defines_a_solver_config():
    """A task on a solver config that no sunnbear module defines runs in a worker, which imports its module."""
    # --- arrange ----------------------
    BenchmarkTaskPool._import_modules([_SAMPLE_SOLVER_CONFIG_MODULE_NAME])
    solver_configs = [SolverConfigRegistry.config_from_id("sample_bisection")]
    cubic = functions.FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(-1.0, 1.0)
    task = BenchmarkTask.from_test_function(
        function=cubic,
        solver_configs=solver_configs,
        run_settings=BenchmarkRunSettings(mc_size=32, n_bisection_fevals=40, root_seed=1),
    )
    task_pool = BenchmarkTaskPool.for_run(n_workers=2, solver_configs=solver_configs, functions=[cubic])

    # --- act --------------------------
    [(key, results)] = list(task_pool.run({"cubic": task}))

    # --- assert -----------------------
    assert key == "cubic"
    assert results["solver_id"].unique().to_list() == ["sample_bisection"]
    assert results["is_correct"].all()


def test_a_run_with_workers_refuses_a_solver_config_defined_in_an_interactive_session(monkeypatch):
    """A config defined in `__main__` without a file cannot be imported by a worker, so only 1 worker is allowed."""
    # --- arrange ----------------------
    monkeypatch.setitem(sys.modules, "__main__", types.ModuleType("__main__"))
    interactive_config = type("InteractiveConfig", (), {"__module__": "__main__"})()

    # --- act / assert -----------------
    BenchmarkTaskPool.for_run(n_workers=1, solver_configs=[interactive_config], functions=[])
    with pytest.raises(ValueError, match="defined in an interactive session"):
        BenchmarkTaskPool.for_run(n_workers=2, solver_configs=[interactive_config], functions=[])
