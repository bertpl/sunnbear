"""`AndersonBjorckMpmathTwin` runs mpmath's Anderson-Björck method as a `Solver`, so `AndersonBjorck` can be tested
against it."""

import math

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
    - mpmath computes the chord's zero as ``a - fa / ((fb - fa) / (b - a))``, a step from mpmath's ``a``, which is
      the bound that does not hold the most recent iterate, where `AndersonBjorck` computes it with `chord_zero`, so
      the iterates can differ in their last bits;
    - mpmath computes the factor as ``1 - f_new / f_previous``, where `AndersonBjorck` computes the ratio of 2 chord
      slopes, as its paper does; the 2 are equal in exact arithmetic for a new iterate at the chord's zero;
    - mpmath takes no step of delta, so the twin takes it in mpmath's place, as `_MpmathFunctionWithStepOfDelta`
      describes.

    On every compared test case, `AndersonBjorck` takes 1 step of delta, its last evaluation: the step crosses the root
    and ends the solve. So the agreement check compares every x-value that mpmath computes, then the step of delta,
    and the root estimate.

    The twin is not compared on the test cases of `steep_exponential`: on that function, both solvers need more
    evaluations than the budget of the twin test cases, and at ``xtol = 1e-4``, `AndersonBjorck` takes steps of delta
    that do not end the solve, after which mpmath cannot continue.
    """

    name = "anderson_bjorck_mpmath_twin"
    version = 1
    n_reevaluated_bounds = 2
    excluded_test_cases = frozenset(test_case for test_case in TWIN_TEST_CASES if test_case.f is steep_exponential)

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Iterate mpmath's solver, with the step of delta taken in mpmath's place; a tolerance of 0 disables mpmath's
        own stopping test on |f|."""
        f_with_step_of_delta = _MpmathFunctionWithStepOfDelta(f, a, b, xtol, self.n_reevaluated_bounds)
        # mpmath's `Illinois` class also runs the Illinois and Pegasus methods; `method="anderson"` picks the
        # Anderson-Björck scaling of the retained bound.
        for _ in MpmathIllinois(mpmath.fp, f_with_step_of_delta, [a, b], tol=0.0, verbose=False, method="anderson"):
            pass


# ==================================================================================================
#  _MpmathFunctionWithStepOfDelta
# ==================================================================================================
class _MpmathFunctionWithStepOfDelta:
    """`_MpmathFunctionWithStepOfDelta` is `AndersonBjorckMpmathTwin`'s function argument to mpmath: where mpmath asks
    for ``f`` at a chord's zero that lies within ``xtol`` of its most recent iterate, it evaluates `AndersonBjorck`'s
    step of delta instead, ``xtol`` from that iterate toward the retained bound.

    It follows mpmath's 2 points as mpmath updates them: ``b``, the most recent iterate, and ``a``, the retained bound,
    which mpmath replaces by the previous ``b`` when ``f`` at the new iterate and at ``b`` differ in sign.

    mpmath takes the returned function value as the value at its own chord's zero, so it cannot continue after a step
    of delta. The step therefore has to end the solve, by `TwinConvergedSignal`; a step that does not end it raises an
    error.
    """

    def __init__(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float, n_reevaluated_bounds: int) -> None:
        """Start from mpmath's initial points, with ``b`` as the most recent iterate.

        The first ``n_reevaluated_bounds`` calls are mpmath's own evaluations of ``a`` and ``b``, which pass through
        without a step of delta.
        """
        self._f = f
        self._xtol = xtol
        self._a, self._b = a, b
        self._fb = 0.0  # mpmath evaluates a, then b, so after its evaluations of the bounds this field holds f(b).
        self._n_reevaluated_bounds_left = n_reevaluated_bounds

    def __call__(self, x: float) -> float:
        """Return ``f(x)``, or ``f`` at `AndersonBjorck`'s step of delta where `AndersonBjorck` takes one."""
        # --- mpmath's evaluations of a and b ----
        if self._n_reevaluated_bounds_left > 0:
            self._n_reevaluated_bounds_left -= 1
            self._fb = self._f(x)
            return self._fb
        else:
            # --- an iterate ---------------------
            is_step_of_delta = abs(x - self._b) < self._xtol
            if is_step_of_delta:
                x = self._b - self._xtol * math.copysign(1.0, self._b - self._a)
            fx = self._f(x)  # This raises TwinConvergedSignal once `AndersonBjorck` stops.
            if is_step_of_delta:
                raise AssertionError("A step of delta did not end the solve, so mpmath cannot continue from it.")
            if fx * self._fb < 0.0:  # This is mpmath's own test for a new iterate on the other side of the root.
                self._a = self._b
            self._b, self._fb = x, fx
            return fx
