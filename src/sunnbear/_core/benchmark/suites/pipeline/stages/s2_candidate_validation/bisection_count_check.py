"""The bisection count check rejects a candidate unless `Bisection` spends exactly `DEFAULT_N_BISECTION_FEVALS`.

Bisection's evaluation count is the benchmark's reference cost, so the check accepts a candidate only when `Bisection`
converges in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations at every tuple of the shipped tuple set's largest size.
Each tuple maps onto ``xtol`` and ``c`` as in a benchmark run.

The check is strict in both directions: it rejects a candidate on which a solve ends early, at a midpoint where f is
exactly 0, as well as one on which a solve spends 1 evaluation too many.

The check at `DEFAULT_N_BISECTION_FEVALS` also covers every smaller `n_bisection_fevals`:

- **Ending early:** for a given ``c``, bisection evaluates the same midpoints in the same order whatever ``xtol``
  is, and ``xtol`` only decides when it stops. So a solve with a smaller `n_bisection_fevals` evaluates only the first
  midpoints of the solve at `DEFAULT_N_BISECTION_FEVALS`, and an exact 0 that ends the smaller solve early also ends
  the solve at `DEFAULT_N_BISECTION_FEVALS` early, which the check rejects.
- **1 evaluation too many:** `compute_xtol_range` keeps the `xtol` range a margin away from both edges of the range in
  exact arithmetic, and sizes that margin for each `n_bisection_fevals`, so that bisection never spends 1 evaluation
  too many.
"""

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, compute_solve_settings
from sunnbear._core.problems.core import TestProblem
from sunnbear._core.solvers.bracketing import Bisection
from sunnbear._core.solvers.core import SolveStatus


def is_bisection_count_exact(problem: TestProblem, *, mc_tuples: MCTuples) -> bool:
    """Return whether `Bisection` converges in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations at every tuple.

    Each tuple of `mc_tuples` maps onto ``xtol`` within the range from `compute_xtol_range`, and onto ``c`` within the
    c-range of `problem`. `mc_tuples` must be the largest size of the shipped tuple set, of which every smaller size is
    a prefix. The check runs 1 solve per tuple and stops at the first tuple with another count or a solve that does not
    converge.
    """
    xtols, cs, max_fevals = compute_solve_settings(
        problem, mc_tuples=mc_tuples, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS
    )
    solver = Bisection()
    for xtol, c in zip(xtols, cs, strict=True):
        result = solver.solve(
            problem.build_x_fun(float(c)), problem.a, problem.b, xtol=float(xtol), max_fevals=max_fevals
        )
        if result.status is not SolveStatus.CONVERGED or result.n_fevals != DEFAULT_N_BISECTION_FEVALS:
            return False
    return True
