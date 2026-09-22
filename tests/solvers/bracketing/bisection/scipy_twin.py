"""`BisectionScipyTwin` runs `scipy.optimize.bisect` as a `Solver`, so `Bisection` can be tested against it.

A twin exists for agreement tests only: it is never registered, never benchmarked, and SciPy runs on
plain floats, so the twin's flop counts hold only the framework's own checks. SciPy evaluates ``f`` at the
interval bounds itself, so the twin's ``n_fevals`` is 2 more than SciPy's own function-call count.
"""

import scipy.optimize

from sunnbear.solvers import Solver, SolveState


class BisectionScipyTwin(Solver):
    """`BisectionScipyTwin` hands the interval to `scipy.optimize.bisect` and returns its root."""

    name = "bisection_scipy_twin"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Run SciPy's bisect; every evaluation still goes through ``state.f``, so it is counted and capped."""
        a, b = float(state.interval.a), float(state.interval.b)
        x, _ = scipy.optimize.bisect(lambda x: float(state.f(x)), a, b, xtol=float(state.xtol), full_output=True)
        return x
