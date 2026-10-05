"""`IllinoisMpmathTwin` runs mpmath's Illinois method as a `Solver`, so `Illinois` can be tested against it."""

import mpmath
from mpmath.calculus.optimization import Illinois as MpmathIllinois

from sunnbear.solvers import SolveState
from tests.solvers.twins import TwinConverged, TwinFunction, TwinSolver


class IllinoisMpmathTwin(TwinSolver):
    """`IllinoisMpmathTwin` runs mpmath's Illinois method on the interval and returns the root estimate at the point
    where `Illinois` would stop.

    mpmath implements the Illinois method and 2 related methods as 1 solver class whose `method` keyword picks how
    the function value is scaled at the bound that the interval keeps.

    The twin runs that class in mpmath's float64 context, `mpmath.fp`, so its arithmetic is plain float64. It
    deviates from exact agreement in these declared ways:

    - mpmath evaluates both interval bounds again before its first iterate;
    - mpmath computes the chord's zero as ``a - fa / ((fb - fa) / (b - a))``, a step from ``a``, where `Illinois`
      uses regula falsi's ``(a * fb - b * fa) / (fb - fa)``, so the iterates can differ in their last bits.
    """

    name = "illinois_mpmath_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _solve(self, state: SolveState) -> float:
        """Iterate mpmath's solver through a `TwinFunction`, which stops it where `Illinois` would stop."""
        f = TwinFunction(state, self.n_reevaluated_bounds)
        interval = [float(state.interval.a), float(state.interval.b)]
        # A tolerance of 0 disables mpmath's own stopping test on |f|, so TwinConverged always ends the loop.
        try:
            for _ in MpmathIllinois(mpmath.fp, f, interval, tol=0.0, verbose=False, method="illinois"):
                pass
        except TwinConverged as converged:
            return converged.x
        raise AssertionError("mpmath's loop ended before sunnbear's stopping criterion held.")
