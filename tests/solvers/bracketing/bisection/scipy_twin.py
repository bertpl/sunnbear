"""`BisectionScipyTwin` runs `scipy.optimize.bisect` as a `Solver`, so `Bisection` can be tested against it."""

import scipy.optimize

from tests.solvers.twins import StoppingWrappedFunction, TwinSolver


class BisectionScipyTwin(TwinSolver):
    """`BisectionScipyTwin` hands the interval to `scipy.optimize.bisect` and returns the root estimate at the point
    where `Bisection` would stop.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first midpoint;
    - SciPy computes each midpoint as the lower bound plus a halved step, where `Bisection` averages the 2 bounds,
      so the midpoints can differ in their last bits.
    """

    name = "bisection_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's bisect; its own stopping test on xtol and rtol is met later than Bisection's."""
        scipy.optimize.bisect(f, a, b, xtol=xtol)
