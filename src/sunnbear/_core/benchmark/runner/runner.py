"""`run_benchmark` runs solvers on test functions over the Monte Carlo samples, writing the results to a run directory.

A run is 1 `BenchmarkTask` per test function, run by a `BenchmarkWorkerPool` in worker processes. Each task's
results are written to a file of their own under the run directory's `staging/` as the task finishes, and a
formula's results file is written as soon as all of the formula's test functions have finished.

The run info is written before the first task, so a call that resumes the run can check its inputs and
versions against the stored run info.

`load_results` reads 1 or more finished runs back as 1 table. The run directory's layout is described by
`BenchmarkRunDir`.
"""

import itertools
from collections.abc import Sequence
from pathlib import Path

import polars as pl

from sunnbear._core.benchmark.protocol import N_BISECTION_FEVALS
from sunnbear._core.functions.core import TestFunction
from sunnbear._core.solvers.core import SolverConfig

from .run_dir import BenchmarkRunDir
from .run_info import BenchmarkRunInfo
from .run_settings import BenchmarkRunSettings
from .task import BenchmarkTask
from .worker_pool import BenchmarkWorkerPool

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
    n_workers: int | None = None,
) -> None:
    """Run every solver config on every calibrated test function over `mc_size` Monte Carlo samples, into `run_dir`.

    When `run_dir` holds no run, the run starts there. When `run_dir` holds a run, the call resumes that run:

    - a formula whose results file exists is skipped;
    - within the other formulas, a test function whose results are already stored in the run directory is
      skipped.

    A run only resumes with the same inputs, and with the same package and data artifact versions, because
    its results depend on them. Resuming a finished run changes nothing. The number of workers does not
    change the results, so a run may resume with another `n_workers`.

    Args:
        solver_configs: The solver configs to run; their order is the order of each sample's result rows.
        functions: The calibrated test functions to run, each with its c-range. Their result rows are grouped by
            formula, formulas in order of first appearance, not in the order passed.
        run_dir: The run directory, created when it does not exist.
        root_seed: The run's root seed, from which every seed of the run is derived.
        mc_size: The size of the Monte Carlo tuple set, 1 of `MCTuplesSize`.
        n_bisection_fevals: Bisection's evaluation count, from which the `xtol` range and the evaluation
            budget follow.
        n_workers: The number of worker processes; ``None`` for 1 per CPU, and 1 to run every task in this
            process. Each worker imports the modules that define the formulas and solver configs, and a class
            defined in an interactive session has no module file to import, so with more than 1 worker, no
            formula or solver config may be defined in an interactive session. Every worker also runs the main
            script again, so a script that runs more than 1 worker must call `run_benchmark` under
            `if __name__ == "__main__":`.

    Raises:
        ValueError: If an input is invalid, which leaves `run_dir` unwritten:

            - `solver_configs` or `functions` is empty or holds an id twice;
            - `mc_size` is not 1 of `MCTuplesSize`;
            - `n_bisection_fevals` is below 2;
            - `n_workers` is below 1, or above 1 while a formula or solver config is defined in an
              interactive session.

        BenchmarkRunError: If `run_dir` holds a malformed run info, or a run with other inputs or versions.
    """
    run_settings = BenchmarkRunSettings(mc_size=mc_size, n_bisection_fevals=n_bisection_fevals, root_seed=root_seed)
    worker_pool = BenchmarkWorkerPool.for_run(n_workers=n_workers, solver_configs=solver_configs, functions=functions)
    benchmark_run_dir = BenchmarkRunDir(run_dir)
    run_info = benchmark_run_dir.store_or_check_run_info(
        BenchmarkRunInfo.for_current_inputs(
            run_settings=run_settings, solver_configs=solver_configs, functions=functions
        )
    )

    # --- collect the unfinished tasks -----------
    tasks: dict[tuple[str, int], BenchmarkTask] = {}
    n_functions_by_formula_id: dict[str, int] = {}
    for formula_id in run_info.formula_ids:
        if benchmark_run_dir.has_formula_results(formula_id):
            continue
        formula_functions = [function for function in functions if function.id.formula_id == formula_id]
        n_functions_by_formula_id[formula_id] = len(formula_functions)
        for function_idx, function in enumerate(formula_functions):
            if not benchmark_run_dir.has_staged_function_results(formula_id, function_idx):
                tasks[formula_id, function_idx] = BenchmarkTask.from_test_function(
                    function=function, solver_configs=solver_configs, run_settings=run_settings
                )

    # --- run the tasks, write results files -----
    # A run that stopped after staging the results of a formula's last test function has only the formula's
    # results file left to write.
    for formula_id, n_functions in n_functions_by_formula_id.items():
        benchmark_run_dir.write_formula_results_if_all_staged(formula_id, n_functions)
    for (formula_id, function_idx), results in worker_pool.run(tasks):
        benchmark_run_dir.stage_function_results(formula_id, function_idx, results)
        benchmark_run_dir.write_formula_results_if_all_staged(formula_id, n_functions_by_formula_id[formula_id])

    benchmark_run_dir.mark_finished(run_info)


# ==================================================================================================
#  load_results
# ==================================================================================================
def load_results(run_dirs: Path | Sequence[Path]) -> pl.LazyFrame:
    """Return a lazy frame over the results of 1 or more finished runs, 1 row per solve.

    The rows of several runs follow each other in the order of `run_dirs`. Every pair of runs must pass
    `BenchmarkRunInfo.check_combinable_with`: everything that their results depend on must be the same, except
    that the runs may cover different solvers and test functions.

    A query on the frame reads only the files, row groups and columns that it needs. The columns and their
    types are those of `RESULTS_SCHEMA`.

    Raises:
        ValueError: If `run_dirs` is an empty sequence.
        BenchmarkRunError: If a run directory holds no run, a malformed run info, or a run that is not
            finished, or if `BenchmarkRunInfo.check_combinable_with` refuses 2 of the runs.
    """
    if isinstance(run_dirs, Path):
        benchmark_run_dirs = [BenchmarkRunDir(run_dirs)]
    else:
        benchmark_run_dirs = [BenchmarkRunDir(run_dir) for run_dir in run_dirs]
    if not benchmark_run_dirs:
        raise ValueError("run_dirs must hold at least 1 run directory.")

    for benchmark_run_dir, other_benchmark_run_dir in itertools.combinations(benchmark_run_dirs, 2):
        benchmark_run_dir.check_combinable_with(other_benchmark_run_dir)
    return pl.concat([benchmark_run_dir.scan_results() for benchmark_run_dir in benchmark_run_dirs])
