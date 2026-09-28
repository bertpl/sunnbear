"""`run_benchmark` runs solvers on test functions over the Monte Carlo samples and writes the results to a run folder.

A run is 1 `BenchmarkTask` per test function, run in this process, formula by formula. Each formula's
results file is written once all of its test functions have run, so a crashed run resumes with the
formulas that have no results file yet. The run info is written before the first task, so a resumed run
is checked against the run that it resumes.

`load_results` reads a finished run back. The run folder's layout is described by `BenchmarkRunFolder`.
"""

from collections.abc import Sequence
from pathlib import Path

import polars as pl

from sunnbear._core.functions.core import TestFunction
from sunnbear._core.solvers.core import SolverConfig

from .run_folder import BenchmarkRunFolder
from .run_info import BenchmarkRunInfo
from .run_settings import BenchmarkRunSettings
from .task import BenchmarkTask
from .tolerances import N_BISECTION_FEVALS

# A run's default Monte Carlo tuple set size is the number of samples per (solver, test function) pair.
DEFAULT_MC_SIZE = 256


# ==================================================================================================
#  run_benchmark
# ==================================================================================================
def run_benchmark(
    *,
    solver_configs: Sequence[SolverConfig],
    functions: Sequence[TestFunction],
    run_dir: Path,
    root_seed: int,
    mc_size: int = DEFAULT_MC_SIZE,
    n_bisection_fevals: int = N_BISECTION_FEVALS,
) -> None:
    """Run every solver config on every calibrated test function over `mc_size` Monte Carlo samples, into `run_dir`.

    When `run_dir` holds no run, the run starts there. When it holds a run, the call resumes it:

    - a formula whose results file exists is skipped;
    - within the other formulas, a test function whose results are already stored in the run folder is
      skipped.

    A run only resumes with the same inputs, and with the same package and data artifact versions, because
    its results depend on them. Resuming a finished run changes nothing.

    Args:
        solver_configs: The solver configs to run; their order is the order of each sample's result rows.
        functions: The calibrated test functions to run, each with its c-range. They run grouped by formula,
            formulas in order of first appearance, so the result rows follow that order, not the order passed.
        run_dir: The run folder, created when it does not exist.
        root_seed: The run's root seed, from which every seed of the run is derived.
        mc_size: The size of the Monte Carlo tuple set, 1 of `MC_TUPLES_SIZES`.
        n_bisection_fevals: Bisection's evaluation count, from which the `xtol` range and the evaluation
            budget follow.

    Raises:
        ValueError: If an input is invalid, which leaves `run_dir` unwritten:

            - `solver_configs` or `functions` is empty or holds an id twice;
            - `mc_size` is not 1 of `MC_TUPLES_SIZES`;
            - `n_bisection_fevals` is below 2.

        BenchmarkRunError: If `run_dir` holds a run with other inputs or versions.
    """
    run_settings = BenchmarkRunSettings(mc_size=mc_size, n_bisection_fevals=n_bisection_fevals, root_seed=root_seed)
    run_folder = BenchmarkRunFolder(run_dir)
    run_info = run_folder.start_or_resume(
        BenchmarkRunInfo.for_new_run(run_settings=run_settings, solver_configs=solver_configs, functions=functions)
    )

    for formula_id, formula_functions in _group_by_formula(functions).items():
        if run_folder.has_formula_results(formula_id):
            continue
        for function_idx, function in enumerate(formula_functions):
            if not run_folder.has_staged_function_results(formula_id, function_idx):
                task = BenchmarkTask.from_test_function(
                    function=function, solver_configs=solver_configs, run_settings=run_settings
                )
                run_folder.stage_function_results(formula_id, function_idx, task.run())
        run_folder.write_formula_results(formula_id, len(formula_functions))

    if not run_info.is_finished:
        run_folder.write_run_info(run_info.with_finished_at_now())


# ==================================================================================================
#  load_results
# ==================================================================================================
def load_results(run_dir: Path) -> pl.LazyFrame:
    """Return a lazy frame over the results of the finished run in `run_dir`, 1 row per solve.

    A query on the frame reads only the files, row groups and columns that it needs. The columns and their
    types are those of `RESULTS_SCHEMA`.

    Raises:
        BenchmarkRunError: If `run_dir` holds no run, or a run that is not finished.
    """
    return BenchmarkRunFolder(run_dir).scan_results()


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _group_by_formula(functions: Sequence[TestFunction]) -> dict[str, list[TestFunction]]:
    """Return the test functions grouped by formula id, formulas in order of first appearance, each group in order."""
    functions_by_formula: dict[str, list[TestFunction]] = {}
    for function in functions:
        functions_by_formula.setdefault(function.id.formula_id, []).append(function)
    return functions_by_formula
