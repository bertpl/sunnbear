"""The bisection count check, validation's third check, rejects a candidate on which bisection spends any other count.

Bisection's evaluation count is the benchmark's reference cost, so on a candidate that the check accepts, `Bisection`
converges in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations at every tuple of the largest size of the shipped tuple
set. Each tuple maps onto ``xtol`` and ``c`` as in a benchmark run. The check is strict in both directions: a solve that
ends early, at a midpoint where f is exactly 0, rejects the candidate as surely as a solve with 1 evaluation too many.

The check at `DEFAULT_N_BISECTION_FEVALS` also covers every smaller `n_bisection_fevals`:

- **Fewer evaluations:** for a given ``c``, bisection evaluates the same midpoints in the same order whatever ``xtol``
  is, and ``xtol`` only decides when it stops. So a solve with a smaller `n_bisection_fevals` evaluates the first
  midpoints of the solve at the default, and an exact 0 that ends it early also ends the solve at the default.
- **More evaluations:** `compute_xtol_range` sizes its margin for each `n_bisection_fevals`, so that bisection never
  spends 1 evaluation too many.
"""

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, compute_xtol_range, max_fevals_for
from sunnbear._core.problems.core import TestProblem
from sunnbear._core.solvers.bracketing import Bisection
from sunnbear._core.solvers.core import SolveStatus


def is_bisection_count_exact(problem: TestProblem, *, mc_tuples: MCTuples) -> bool:
    """Return whether `Bisection` converges in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations at every tuple.

    Each tuple of `mc_tuples` maps onto ``xtol`` within the range from `compute_xtol_range`, and onto ``c`` within the
    c-range of `problem`. The check stops at the first tuple with another count.
    """
    xtol_min, xtol_max = compute_xtol_range(a=problem.a, b=problem.b, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)
    xtols, cs = mc_tuples.to_xtol_and_c(xtol_min=xtol_min, xtol_max=xtol_max, c_min=problem.c_min, c_max=problem.c_max)
    max_fevals = max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)
    solver = Bisection()
    for xtol, c in zip(xtols, cs, strict=True):
        result = solver.solve(
            problem.build_x_fun(float(c)), problem.a, problem.b, xtol=float(xtol), max_fevals=max_fevals
        )
        if result.status is not SolveStatus.CONVERGED or result.n_fevals != DEFAULT_N_BISECTION_FEVALS:
            return False
    return True
