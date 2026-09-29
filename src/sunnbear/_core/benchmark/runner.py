"""`run_benchmark` runs solvers on test functions over the Monte Carlo samples, writing the results to a run directory.

A run is 1 `BenchmarkTask` per test function, run in this process, formula by formula.

The run info is written before the first task, so a call that resumes the run can check its inputs and
versions against the stored run info.

`load_results` reads a finished run back. The run directory's layout is described by `BenchmarkRunDir`.
"""

from collections.abc import Sequence
from pathlib import Path

import polars as pl

from sunnbear._core.functions.core import TestFunction
from sunnbear._core.solvers.core import SolverConfig

from .run_dir import BenchmarkRunDir
from .run_info import BenchmarkRunInfo
from .run_settings import BenchmarkRunSettings
from .task import BenchmarkTask
from .tolerances import N_BISECTION_FEVALS

# The default size of a run's Monte Carlo tuple set, which is the number of samples per (solver, test function) pair.
DEFAULT_MC_SIZE = 256

# The default root seed of a run, from which every seed of the run is derived.
DEFAULT_ROOT_SEED = 42


# ==================================================================================================
#  run_benchmark
# ==================================================================================================
def run_benchmark(
    *,
    solver_configs: Sequence[SolverConfig],
    functions: Sequence[TestFunction],
    run_dir: Path,
    root_seed: int = DEFAULT_ROOT_SEED,
    mc_size: int = DEFAULT_MC_SIZE,
    n_bisection_fevals: int = N_BISECTION_FEVALS,
) -> None:
    """Run every solver config on every calibrated test function over `mc_size` Monte Carlo samples, into `run_dir`.

    When `run_dir` holds no run, the run starts there. When `run_dir` holds a run, the call resumes that run:

    - a formula whose results file exists is skipped;
    - within the other formulas, a test function whose results are already stored in the run directory is
      skipped.

    A run only resumes with the same inputs, and with the same package and data artifact versions, because
    its results depend on them. Resuming a finished run changes nothing.

    Args:
        solver_configs: The solver configs to run; their order is the order of each sample's result rows.
        functions: The calibrated test functions to run, each with its c-range. They run grouped by formula,
            formulas in order of first appearance, so the result rows follow that order, not the order passed.
        run_dir: The run directory, created when it does not exist.
        root_seed: The run's root seed, from which every seed of the run is derived.
        mc_size: The size of the Monte Carlo tuple set, 1 of `MCTuplesSize`.
        n_bisection_fevals: Bisection's evaluation count, from which the `xtol` range and the evaluation
            budget follow.

    Raises:
        ValueError: If an input is invalid, which leaves `run_dir` unwritten:

            - `solver_configs` or `functions` is empty or holds an id twice;
            - `mc_size` is not 1 of `MCTuplesSize`;
            - `n_bisection_fevals` is below 2.

        BenchmarkRunError: If `run_dir` holds a malformed run info, or a run with other inputs or versions.
    """
    run_settings = BenchmarkRunSettings(mc_size=mc_size, n_bisection_fevals=n_bisection_fevals, root_seed=root_seed)
    benchmark_run_dir = BenchmarkRunDir(run_dir)
    run_info = benchmark_run_dir.store_or_check_run_info(
        BenchmarkRunInfo.for_current_inputs(
            run_settings=run_settings, solver_configs=solver_configs, functions=functions
        )
    )

    for formula_id in run_info.formula_ids:
        if benchmark_run_dir.has_formula_results(formula_id):
            continue
        formula_functions = [function for function in functions if function.id.formula_id == formula_id]
        for function_idx, function in enumerate(formula_functions):
            if not benchmark_run_dir.has_staged_function_results(formula_id, function_idx):
                task = BenchmarkTask.from_test_function(
                    function=function, solver_configs=solver_configs, run_settings=run_settings
                )
                benchmark_run_dir.stage_function_results(formula_id, function_idx, task.run())
        benchmark_run_dir.write_formula_results(formula_id, len(formula_functions))

    benchmark_run_dir.mark_finished(run_info)


# ==================================================================================================
#  load_results
# ==================================================================================================
def load_results(run_dir: Path) -> pl.LazyFrame:
    """Return a lazy frame over the results of the finished run in `run_dir`, 1 row per solve.

    A query on the frame reads only the files, row groups and columns that it needs. The columns and their
    types are those of `RESULTS_SCHEMA`.

    Raises:
        BenchmarkRunError: If `run_dir` holds no run, a malformed run info, or a run that is not finished.
    """
    return BenchmarkRunDir(run_dir).scan_results()
