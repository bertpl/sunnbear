"""`AndersonBjorckMpmathTwin` runs mpmath's Anderson-Björck method as a `Solver`, so `AndersonBjorck` can be tested
against it."""

import mpmath
from mpmath.calculus.optimization import Illinois as MpmathIllinois

from tests.solvers.example_functions import steep_exponential
from tests.solvers.twins import TWIN_TEST_CASES, StoppingWrappedFunction, TwinSolver


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

    The twin is not compared on the test cases on `steep_exponential`: there, both solvers need more evaluations
    than the budget of the twin test cases, and the last-bit differences grow to thousands of ulps.
    """

    name = "anderson_bjorck_mpmath_twin"
    version = 1
    n_reevaluated_bounds = 2
    excluded_test_cases = frozenset(test_case for test_case in TWIN_TEST_CASES if test_case.f is steep_exponential)

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Iterate mpmath's solver; a tolerance of 0 disables mpmath's own stopping test on |f|."""
        # mpmath's `Illinois` class also runs the Illinois and Pegasus methods; `method="anderson"` picks the
        # Anderson-Björck scaling of the retained bound.
        for _ in MpmathIllinois(mpmath.fp, f, [a, b], tol=0.0, verbose=False, method="anderson"):
            pass
