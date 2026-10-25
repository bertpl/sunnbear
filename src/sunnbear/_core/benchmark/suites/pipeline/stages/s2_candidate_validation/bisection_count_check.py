"""The bisection count check rejects a candidate unless `Bisection` spends `DEFAULT_N_BISECTION_FEVALS` evaluations.

Bisection's evaluation count is the benchmark's reference cost, so the check accepts a candidate only when `Bisection`
converges in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations at every tuple of the largest size of the shipped tuple
set. Each tuple maps onto ``xtol`` and ``c`` as in a benchmark run.

The check is strict in both directions: it rejects a candidate on which a solve ends early, at a midpoint where f is
exactly 0, as well as one on which a solve spends 1 evaluation too many.

The check at `DEFAULT_N_BISECTION_FEVALS` also covers every smaller `n_bisection_fevals`:

- **Ending early:** for a given ``c``, bisection evaluates the same midpoints in the same order whatever ``xtol``
  is, and ``xtol`` only decides when bisection stops. So a solve with a smaller `n_bisection_fevals` evaluates only the
  first midpoints of the solve at `DEFAULT_N_BISECTION_FEVALS`, and an exact 0 that ends the smaller solve early also
  ends the solve at `DEFAULT_N_BISECTION_FEVALS` early, which the check rejects.
- **1 evaluation too many:** `compute_xtol_range` moves each bound of the `xtol` range inward from its value in exact
  arithmetic by a margin, and sizes that margin for each `n_bisection_fevals`, so that bisection never spends 1
  evaluation too many.
"""

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, compute_solve_settings
from sunnbear._core.problems.core import TestProblem
from sunnbear._core.solvers.bracketing import Bisection
from sunnbear._core.solvers.core import SolveStatus


def is_bisection_count_exact(problem: TestProblem) -> bool:
    """Return whether `Bisection` converges in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations at every tuple.

    The tuples are the largest size of the shipped tuple set, of which every smaller size is a prefix. Each tuple maps
    onto ``xtol`` and ``c`` through `compute_solve_settings`, as in a benchmark run.

    The check runs 1 solve per tuple and stops at the first tuple with another count or a solve that does not converge.
    """
    mc_tuples = load_mc_tuples(max(MCTuplesSize))
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
