"""`BisectionScipyTwin` runs `scipy.optimize.bisect` as a `Solver`, so `Bisection` can be tested against it."""

import scipy.optimize

from sunnbear.solvers import SolveState
from tests.solvers.twins import TwinConverged, TwinFunction, TwinSolver


class BisectionScipyTwin(TwinSolver):
    """`BisectionScipyTwin` hands the interval to `scipy.optimize.bisect` and returns the root estimate at the point
    where `Bisection` would stop.

    SciPy runs on plain floats, so the twin's flop counts hold only the framework's own checks.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first midpoint;
    - SciPy computes each midpoint as the lower bound plus a halved step, where `Bisection` averages the 2 bounds,
      so the midpoints can differ in their last bits.
    """

    name = "bisection_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _solve(self, state: SolveState) -> float:
        """Run SciPy's bisect through a `TwinFunction`, which stops it where `Bisection` would stop."""
        f = TwinFunction(state, self.n_reevaluated_bounds)
        try:
            # SciPy's own stopping test on xtol and rtol is met later than Bisection's, so TwinConverged ends the loop.
            return scipy.optimize.bisect(f, float(state.interval.a), float(state.interval.b), xtol=float(state.xtol))
        except TwinConverged as converged:
            return converged.x
