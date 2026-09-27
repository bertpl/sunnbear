"""`run_benchmark_task` runs 1 benchmark task: every solver over every Monte Carlo sample of 1 test function.

A task needs nothing beyond its own inputs, so tasks can run in separate worker processes.
"""

import time
from collections.abc import Sequence

import polars as pl

from sunnbear._core.functions.core import TestFunction
from sunnbear._core.solvers.core import SolverConfig, SolveStatus

from .correctness import is_solution_correct
from .mc_tuples import MCTuples
from .results_schema import RESULTS_SCHEMA, flops_column_name
from .seeds import SeedPurpose, derive_seed
from .tolerances import compute_xtol_range, max_fevals_for


def run_benchmark_task(
    *,
    function: TestFunction,
    solver_configs: Sequence[SolverConfig],
    mc_tuples: MCTuples,
    n_bisection_fevals: int,
    root_seed: int,
) -> pl.DataFrame:
    """Solve `function` with every solver at every Monte Carlo sample, and return 1 row per solve.

    Each sample maps its (u, v) tuple to a tolerance `xtol` within the `xtol` range derived from
    `n_bisection_fevals` by `compute_xtol_range`, and to a value of the function's parameter `c` within
    `[function.c_min, function.c_max]`.

    Every solver solves `f(x, c)` on the function's interval with that tolerance, within the evaluation
    budget that `max_fevals_for` derives from `n_bisection_fevals`, and the solve is timed on a monotonic
    clock. The timed span includes recording every evaluated x-value, which the correctness check probes
    first, as `x_candidates`.

    A solve that reports convergence is checked with `is_solution_correct`; a solve with any other status
    is not checked, and its row's `is_correct` is `False`.

    The random x-values of the check are seeded per test function and sample, so all solvers of a sample
    are checked against the same random x-values.

    Args:
        function: A calibrated test function.
        solver_configs: The solvers to run; each config is instantiated once and its solver reused for every sample.
        mc_tuples: The Monte Carlo samples; their count is the `size` column.
        n_bisection_fevals: Bisection's evaluation count, from which the `xtol` range and the evaluation
            budget follow.
        root_seed: The run's root seed, from which the seeds of the correctness checks are derived.

    Returns:
        One row per (sample, solver) pair, sample by sample, with the columns and types of `RESULTS_SCHEMA`.
    """
    # --- per-task values ------------------------
    # `to_xtol_and_c` spans the range from its lower bound alone, so the upper bound is not needed.
    xtol_min, _ = compute_xtol_range(a=function.a, b=function.b, n_bisection_fevals=n_bisection_fevals)
    max_fevals = max_fevals_for(n_bisection_fevals=n_bisection_fevals)
    xtols, cs = mc_tuples.to_xtol_and_c(xtol_min, function.c_min, function.c_max)
    function_id = str(function.id)
    configs_and_solvers = [(config, config.instantiate()) for config in solver_configs]

    # --- 1 row per solve ------------------------
    rows = []
    for mc_sample_idx, (u, v, xtol, c) in enumerate(zip(mc_tuples.u, mc_tuples.v, xtols, cs, strict=True)):
        f = function.build_x_fun(float(c))
        seed = derive_seed(
            root_seed=root_seed,
            purpose=SeedPurpose.CORRECTNESS_CHECK,
            function_id=function_id,
            mc_sample_idx=mc_sample_idx,
        )
        for config, solver in configs_and_solvers:
            t_start_ns = time.perf_counter_ns()
            result = solver.solve(
                f, function.a, function.b, xtol=float(xtol), max_fevals=max_fevals, history_enabled=True
            )
            wall_time_ns = time.perf_counter_ns() - t_start_ns
            is_correct = result.status is SolveStatus.CONVERGED and is_solution_correct(
                f=f,
                x_found=result.x,
                xtol=float(xtol),
                seed=seed,
                x_candidates=result.evaluated_x_values,
            )
            rows.append(
                {
                    "solver_id": config.solver_id,
                    "solver_version": config.solver_cls.version,
                    "function_id": function_id,
                    "size": mc_tuples.size,
                    "mc_sample_idx": mc_sample_idx,
                    "u": float(u),
                    "v": float(v),
                    "xtol": float(xtol),
                    "c": float(c),
                    "x_found": result.x,
                    "status": result.status.value,
                    "n_fevals": result.n_fevals,
                    "is_correct": is_correct,
                    "wall_time_ns": wall_time_ns,
                    **{flops_column_name(flop_type): n for flop_type, n in result.flop_counts.as_dict().items()},
                }
            )
    return pl.from_dicts(rows, schema=RESULTS_SCHEMA)
