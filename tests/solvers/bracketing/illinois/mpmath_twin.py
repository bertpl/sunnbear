"""`IllinoisMpmathTwin` runs mpmath's Illinois method as a `Solver`, so `Illinois` can be tested against it."""

import mpmath
from mpmath.calculus.optimization import Illinois as MpmathIllinois

from tests.solvers.twins import TwinFunction, TwinSolver


class IllinoisMpmathTwin(TwinSolver):
    """`IllinoisMpmathTwin` runs mpmath's Illinois method on the interval and returns the root estimate at the point
    where `Illinois` would stop.

    The twin runs mpmath's solver in mpmath's float64 context, `mpmath.fp`, so its arithmetic is plain float64. It
    deviates from exact agreement in these declared ways:

    - mpmath evaluates both interval bounds again before its first iterate;
    - mpmath computes the chord's zero as ``a - fa / ((fb - fa) / (b - a))``, a step from ``a``, where `Illinois`
      uses regula falsi's ``(a * fb - b * fa) / (fb - fa)``, so the iterates can differ in their last bits.
    """

    name = "illinois_mpmath_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: TwinFunction, a: float, b: float, xtol: float) -> None:
        """Iterate mpmath's solver; a tolerance of 0 disables mpmath's own stopping test on |f|."""
        # mpmath's class also runs 2 related methods; `method` picks the Illinois scaling of the retained bound.
        for _ in MpmathIllinois(mpmath.fp, f, [a, b], tol=0.0, verbose=False, method="illinois"):
            pass
