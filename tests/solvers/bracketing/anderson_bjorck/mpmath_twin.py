"""`AndersonBjorckMpmathTwin` runs mpmath's Anderson-Björck method as a `Solver`, so `AndersonBjorck` can be tested
against it."""

import mpmath
from mpmath.calculus.optimization import Illinois as MpmathIllinois

from tests.solvers.twins import StoppingWrappedFunction, TwinSolver


class AndersonBjorckMpmathTwin(TwinSolver):
    """`AndersonBjorckMpmathTwin` runs mpmath's Anderson-Björck method on the interval and returns the root estimate at
    the point where `AndersonBjorck` would stop.

    The twin runs mpmath's solver in mpmath's float64 context, `mpmath.fp`, so its arithmetic is plain float64. The
    twin deviates from exact agreement in these declared ways:

    - mpmath evaluates both interval bounds again before its first iterate;
    - mpmath computes the chord's zero as ``a - fa / ((fb - fa) / (b - a))``, a step from ``a``, where
      `AndersonBjorck` uses regula falsi's ``(a * fb - b * fa) / (fb - fa)``, so the iterates can differ in their last
      bits;
    - in the slow progress that the `AndersonBjorck` class docstring describes, ``1 - f_new / f_previous`` loses about
      8 digits to cancellation, which magnifies the last-bit differences between the 2 chord formulas to differences of
      thousands of ulps in the iterates.
    """

    name = "anderson_bjorck_mpmath_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Iterate mpmath's solver; a tolerance of 0 disables mpmath's own stopping test on |f|."""
        # mpmath's `Illinois` class also runs the Illinois and Pegasus methods; `method="anderson"` picks the
        # Anderson-Björck scaling of the retained bound.
        for _ in MpmathIllinois(mpmath.fp, f, [a, b], tol=0.0, verbose=False, method="anderson"):
            pass
