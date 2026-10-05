"""`BisectionScipyTwin` runs `scipy.optimize.bisect` as a `Solver`, so `Bisection` can be tested against it.

A twin exists for agreement tests only: it is never registered, never benchmarked, and SciPy runs on plain floats,
so the twin's flop counts hold only the framework's own checks.

Declared deviations from exact agreement:

- SciPy evaluates both interval bounds again before its first midpoint;
- SciPy computes each midpoint as the lower bound plus a halved step, where `Bisection` averages the 2 bounds, so
  the midpoints can differ in their last bits.
"""

import scipy.optimize

from sunnbear.solvers import Solver, SolveState
from tests.solvers.twins import TwinConverged, TwinDeviations, TwinFunction

DEVIATIONS = TwinDeviations(n_reevaluated_bounds=2)


class BisectionScipyTwin(Solver):
    """`BisectionScipyTwin` hands the interval to `scipy.optimize.bisect` and returns the root where sunnbear stops."""

    name = "bisection_scipy_twin"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Run SciPy's bisect through a `TwinFunction`, which stops it where `Bisection` would stop."""
        f = TwinFunction(state, DEVIATIONS.n_reevaluated_bounds)
        try:
            # SciPy's own stopping test, on xtol and rtol, holds only after sunnbear's, so TwinConverged ends the loop.
            return scipy.optimize.bisect(f, float(state.interval.a), float(state.interval.b), xtol=float(state.xtol))
        except TwinConverged as converged:
            return converged.x
