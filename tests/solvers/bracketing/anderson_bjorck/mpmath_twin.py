"""`AndersonBjorckMpmathTwin` runs mpmath's Anderson-Björck method as a `Solver`, so `AndersonBjorck` can be tested
against it."""

import mpmath
from mpmath.calculus.optimization import Illinois as MpmathIllinois

from sunnbear.solvers import Interval, IntervalBound
from tests.solvers.example_functions import steep_exponential
from tests.solvers.twins import TWIN_TEST_CASES, StoppingWrappedFunction, TwinSolver


class AndersonBjorckMpmathTwin(TwinSolver):
    """`AndersonBjorckMpmathTwin` runs mpmath's Anderson-Björck method on the interval and returns the root estimate at
    the point where `AndersonBjorck` would stop.

    The twin runs mpmath's solver in mpmath's float64 context, `mpmath.fp`, so its arithmetic is plain float64. The
    twin deviates from exact agreement in these declared ways:

    - mpmath evaluates both interval bounds again before its first iterate;
    - mpmath computes the chord's zero as ``a - fa / ((fb - fa) / (b - a))``, a step from mpmath's ``a``, which is
      the bound that does not hold the most recent iterate, where `AndersonBjorck` computes it with `chord_zero`, so
      the iterates can differ in their last bits;
    - mpmath computes the factor as ``1 - f_new / f_previous``, where `AndersonBjorck` computes the ratio of 2 chord
      slopes, as its paper does; the 2 are equal in exact arithmetic;
    - in the slow progress that the `AndersonBjorck` class docstring describes, the factor loses about 8 digits to
      cancellation in either form, which magnifies the last-bit differences between the 2 implementations to
      differences of thousands of ulps in the iterates.

    The twin stops where `AndersonBjorck` stops, and returns the interval bound with the smaller unscaled ``|f|``.
    `AndersonBjorck` compares the most recent iterate's ``|f|`` with the retained bound's scaled ``|f|``, which the
    twin cannot compute, because the twin sees only the function values at the bounds.

    Wherever the agreement check compares the 2 root estimates to the last bits, the 2 comparisons pick the same
    bound.

    The twin is not compared on the test cases of `steep_exponential`: on that function, both solvers need more
    evaluations than the budget of the twin test cases, and the last-bit differences grow to thousands of ulps.
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

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return the bound with the smaller unscaled ``|f|`` if `AndersonBjorck`'s stopping rule (the interval at most
        ``xtol`` wide, or ``f`` at the best bound 0) holds after the last of ``evaluations``, or ``None`` if it
        continues."""
        (x_best, f_best), (x_other, _) = self._get_bounds_best_estimate_first(interval)
        if abs(x_other - x_best) <= xtol or f_best == 0.0:
            return x_best
        else:
            return None

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _get_bounds_best_estimate_first(interval: Interval) -> tuple[tuple[float, float], tuple[float, float]]:
        """Return the 2 bounds of ``interval`` as ``(x, f(x))`` pairs, the best root estimate first.

        The best root estimate is the bound with the smaller ``|f|``. When both ``|f|`` are equal, the bound that the
        last split replaced, which holds the newest point, comes first.
        """
        if interval.last_replaced_bound is IntervalBound.LOWER:
            x_newest, f_newest, x_other, f_other = interval.a, interval.fa, interval.b, interval.fb
        else:
            x_newest, f_newest, x_other, f_other = interval.b, interval.fb, interval.a, interval.fa
        if abs(f_other) < abs(f_newest):
            return (x_other, f_other), (x_newest, f_newest)
        else:
            return (x_newest, f_newest), (x_other, f_other)
