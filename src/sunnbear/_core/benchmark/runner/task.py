"""`BenchmarkTask` is 1 benchmark task: every solver over every Monte Carlo sample of 1 test problem.

A task holds only ids and plain values, and rebuilds the test problem, the solvers and the Monte Carlo
tuples from them when it runs, so a task can be sent to a worker process as it is.
"""

import time
from collections.abc import Sequence
from dataclasses import dataclass

import polars as pl

from sunnbear._core.benchmark.mc_tuples import load_mc_tuples
from sunnbear._core.benchmark.protocol import (
    SeedPurpose,
    compute_xtol_range,
    derive_seed,
    is_solution_correct,
    max_fevals_for,
)
from sunnbear._core.problems.core import FormulaRegistry, TestProblem
from sunnbear._core.solvers.core import SolverConfig, SolverConfigRegistry, SolveStatus

from .results_schema import RESULTS_SCHEMA, solver_flop_count_column_name
from .run_settings import BenchmarkRunSettings


# ==================================================================================================
#  BenchmarkTask
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class BenchmarkTask:
    """`BenchmarkTask` is 1 benchmark task: every solver over every Monte Carlo sample of 1 test problem.

    Attributes:
        problem_id: The id of the test problem.
        c_min: The lower end of the test problem's calibrated c-range.
        c_max: The upper end of the test problem's calibrated c-range.
        solver_ids: The ids of the solver configs to run, in the order of the result rows.
        run_settings: The settings that every task of the run shares.
    """

    problem_id: str
    c_min: float
    c_max: float
    solver_ids: tuple[str, ...]
    run_settings: BenchmarkRunSettings

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @classmethod
    def from_test_problem(
        cls,
        *,
        problem: TestProblem,
        solver_configs: Sequence[SolverConfig],
        run_settings: BenchmarkRunSettings,
    ) -> "BenchmarkTask":
        """Return the task for a calibrated test problem and solver configs, holding only their ids."""
        return cls(
            problem_id=str(problem.id),
            c_min=problem.c_min,
            c_max=problem.c_max,
            solver_ids=tuple(config.solver_id for config in solver_configs),
            run_settings=run_settings,
        )

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    def run(self) -> pl.DataFrame:
        """Solve the test problem with every solver at every Monte Carlo sample, and return 1 row per solve.

        The test problem, the solver configs and the Monte Carlo tuples are rebuilt from their ids and
        from `run_settings.mc_size`, so every solver config and formula must be registered in the process
        that runs the task.

        Each sample maps its (u, v) tuple to a tolerance `xtol` within the `xtol` range derived from
        `n_bisection_fevals` by `compute_xtol_range`, and to a value of the test problem's parameter `c` within
        `[c_min, c_max]`.

        Every solver solves `f(x, c)` on the test problem's interval with that tolerance, within the evaluation
        budget that `max_fevals_for` derives from `n_bisection_fevals`, and the solve is timed on a monotonic
        clock. The timed span includes recording every evaluated x-value, which the correctness check probes
        first, as `x_candidates`.

        A solve that reports convergence is checked with `is_solution_correct`; a solve with any other status
        is not checked, and its row's `is_correct` is `False`.

        The random x-values of the check are seeded per test problem and sample, so all solvers of a sample
        are checked against the same random x-values.

        Returns:
            One row per (sample, solver) pair, sample by sample, with the columns and types of `RESULTS_SCHEMA`.
        """
        # --- rebuild from ids -----------------------
        problem = FormulaRegistry.candidate_from_id(self.problem_id).calibrated(self.c_min, self.c_max)
        configs_and_solvers = [
            (config, config.instantiate())
            for config in (SolverConfigRegistry.config_from_id(solver_id) for solver_id in self.solver_ids)
        ]
        mc_tuples = load_mc_tuples(self.run_settings.mc_size)

        # --- per-task values ------------------------
        n_bisection_fevals = self.run_settings.n_bisection_fevals
        # `to_xtol_and_c` spans the range from its lower bound alone, so the upper bound is not needed.
        xtol_min, _ = compute_xtol_range(a=problem.a, b=problem.b, n_bisection_fevals=n_bisection_fevals)
        max_fevals = max_fevals_for(n_bisection_fevals=n_bisection_fevals)
        xtols, cs = mc_tuples.to_xtol_and_c(xtol_min, problem.c_min, problem.c_max)

        # --- 1 row per solve ------------------------
        rows = []
        for mc_sample_idx, (u, v, xtol, c) in enumerate(zip(mc_tuples.u, mc_tuples.v, xtols, cs, strict=True)):
            f = problem.build_x_fun(float(c))
            seed = derive_seed(
                root_seed=self.run_settings.root_seed,
                purpose=SeedPurpose.CORRECTNESS_CHECK,
                problem_id=self.problem_id,
                mc_sample_idx=mc_sample_idx,
            )
            for config, solver in configs_and_solvers:
                t_start_ns = time.perf_counter_ns()
                result = solver.solve(
                    f, problem.a, problem.b, xtol=float(xtol), max_fevals=max_fevals, history_enabled=True
                )
                wall_time_ns = time.perf_counter_ns() - t_start_ns
                if result.status is SolveStatus.CONVERGED:
                    is_correct = is_solution_correct(
                        f=f,
                        x_found=result.x,
                        xtol=float(xtol),
                        seed=seed,
                        x_candidates=result.evaluated_x_values,
                    )
                else:
                    is_correct = False

                rows.append(
                    {
                        "solver_id": config.solver_id,
                        "solver_version": config.solver_cls.version,
                        "problem_id": self.problem_id,
                        "mc_size": mc_tuples.size,
                        "mc_sample_idx": mc_sample_idx,
                        "u": float(u),
                        "v": float(v),
                        "xtol": float(xtol),
                        "c": float(c),
                        "max_fevals": max_fevals,
                        "x_found": result.x,
                        "status": result.status.value,
                        "n_fevals": result.n_fevals,
                        "is_correct": is_correct,
                        "wall_time_ns": wall_time_ns,
                        **{
                            solver_flop_count_column_name(flop_type): n
                            for flop_type, n in result.flop_counts.as_dict().items()
                        },
                    }
                )
        return pl.from_dicts(rows, schema=RESULTS_SCHEMA)
