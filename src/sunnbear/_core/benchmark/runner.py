"""`run_benchmark` runs solvers on test functions over the Monte Carlo samples into a run folder; `load_results` reads it.

A run is 1 `BenchmarkTask` per test function, run in this process, formula by formula. Each formula's
results file is written once all of its test functions have run, so a crashed run resumes with the
formulas that have no results file yet. The run folder's layout is described by `BenchmarkRunFolder`.
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

# The default size of the Monte Carlo tuple set of a run: the number of samples per (solver, test function) pair.
DEFAULT_MC_SIZE = 256


# ==================================================================================================
#  run_benchmark
# ==================================================================================================
def run_benchmark(
    *,
    solver_configs: Sequence[SolverConfig],
    functions: Sequence[TestFunction],
    out_dir: Path,
    root_seed: int,
    mc_size: int = DEFAULT_MC_SIZE,
    n_bisection_fevals: int = N_BISECTION_FEVALS,
) -> None:
    """Run every solver config on every calibrated test function over `mc_size` Monte Carlo samples, into `out_dir`.

    When `out_dir` holds no run, the run starts there. When it holds a run, the call resumes it:

    - a formula whose results file exists is skipped;
    - within the other formulas, a test function whose results were staged is skipped.

    A run only resumes with the same inputs, and with the same package and data artifact versions, because
    its results depend on them. Resuming a finished run changes nothing.

    Args:
        solver_configs: The solver configs to run; their order is the order of each sample's result rows.
        functions: The calibrated test functions to run, each with its c-range.
        out_dir: The run folder.
        root_seed: The run's root seed, from which every seed of the run is derived.
        mc_size: The size of the Monte Carlo tuple set, 1 of `MC_TUPLES_SIZES`.
        n_bisection_fevals: Bisection's evaluation count, from which the `xtol` range and the evaluation
            budget follow.

    Raises:
        ValueError: If `solver_configs` or `functions` is empty or holds an id twice, if `mc_size` is not
            1 of `MC_TUPLES_SIZES`, or if `n_bisection_fevals` is below 2.
        BenchmarkRunError: If `out_dir` holds a run with other inputs or versions.
    """
    # --- check the inputs -----------------------
    _check_ids_are_unique("solver_configs", [config.solver_id for config in solver_configs])
    _check_ids_are_unique("functions", [str(function.id) for function in functions])
    run_settings = BenchmarkRunSettings(mc_size=mc_size, n_bisection_fevals=n_bisection_fevals, root_seed=root_seed)

    # --- start or resume the run ----------------
    run_folder = BenchmarkRunFolder(out_dir)
    run_info = BenchmarkRunInfo.for_new_run(
        run_settings=run_settings, solver_configs=solver_configs, functions=functions
    )
    stored_run_info = run_folder.read_run_info()
    if stored_run_info is None:
        run_folder.write_run_info(run_info)
    else:
        stored_run_info.check_resumable_as(run_info)
        run_info = stored_run_info

    # --- run formula by formula -----------------
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
        run_folder.write_run_info(run_info.finished_now())


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
def _check_ids_are_unique(argument_name: str, ids: Sequence[str]) -> None:
    """Check that `ids`, the ids of the items of the argument `argument_name`, are at least 1 and all differ.

    Raises:
        ValueError: If `ids` is empty or holds an id twice.
    """
    if not ids:
        raise ValueError(f"{argument_name} must hold at least 1 item.")
    duplicate_ids = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicate_ids:
        raise ValueError(f"{argument_name} holds these ids more than once: {duplicate_ids}.")


def _group_by_formula(functions: Sequence[TestFunction]) -> dict[str, list[TestFunction]]:
    """Return the test functions grouped by formula id, formulas in order of first appearance, keeping their order."""
    functions_by_formula: dict[str, list[TestFunction]] = {}
    for function in functions:
        functions_by_formula.setdefault(function.id.formula_id, []).append(function)
    return functions_by_formula
