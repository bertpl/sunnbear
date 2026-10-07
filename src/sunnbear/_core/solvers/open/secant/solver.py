"""`Secant` implements the secant method: each step evaluates where the line through the 2 latest points is zero."""

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.exceptions import DivergedError


class Secant(Solver):
    """`Secant` implements the secant method, in the form of SciPy's ``scipy.optimize.newton`` without a derivative.

    Each step computes the zero of the line through the 2 latest points, the secant. Near a simple root, the method
    converges faster than linearly, with order about 1.618.

    `Secant` is an open method: it keeps no interval around the root, so its iterates may leave the initial
    interval, and its result is not guaranteed to lie within ``xtol`` of a root. For this reason, `Secant` subclasses
    `Solver` directly and implements its own loop, not the interval-reducing loop of `BracketingSolver`.

    `Secant` follows SciPy in each respect below except equal function values:

    - **Starting points:** the bounds of the initial interval. The method treats one bound as the older point and the
      other as the newest point, and the newest point is the bound with the larger ``|f|``, or the upper bound when
      both are equal.
    - **Step formula:** the zero of the secant, computed from the ratio of the 2 function values, with the value of
      smaller magnitude divided by the value of larger magnitude, so that the ratio's magnitude is at most 1.
    - **Stopping criterion:** the solve ends once the step from the newest point to the next point is at most
      ``xtol``, and returns that next point without evaluating it.
    - **Equal function values:** when the 2 latest points have equal function values, the secant is horizontal and
      its zero lies at infinity. `Secant` then raises `DivergedError`, which `Solver.solve` records as ``DIVERGED``;
      SciPy returns the midpoint of the 2 points as a result that did not converge.

    A small step does not show that the next point is close to a root: on a function that is nearly flat between 2
    points, a step taken far from the root can be smaller than ``xtol``.

    References:
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section 9.2.
          Cambridge University Press. Its ``rtsec`` takes the bound with the smaller ``|f|`` as the newest point,
          where SciPy and `Secant` take the bound with the larger ``|f|``.
        - SciPy's ``scipy.optimize.newton``, without a derivative; the test suite checks `Secant` against it.
    """

    name = "secant"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Run the secant method from the interval bounds; return the first secant zero within ``xtol`` of its start.

        Each pass computes the zero of the secant through the 2 latest points. If the step from the newest point to that
        zero is at most ``xtol``, the pass returns the zero; otherwise the pass evaluates the zero and makes that zero
        the newest point.

        Raises:
            DivergedError: If the 2 latest points have equal function values, so the next point lies at infinity.
        """
        # --- starting points --------------------
        # x0 and x1 are the 2 latest points, x1 the newest, with function values f0 and f1.
        interval = state.interval
        x0, x1, f0, f1 = interval.a, interval.b, interval.fa, interval.fb
        # The newest point is the bound with the larger |f|, the upper bound when both are equal, as in SciPy.
        if abs(f1) < abs(f0):
            x0, x1, f0, f1 = x1, x0, f1, f0
        state.x_best = x1

        # --- main loop --------------------------
        while True:
            if f1 == f0:
                raise DivergedError("The 2 latest points have equal function values, so the next point is infinite.")
            # Divide the smaller |f| by the larger, as SciPy does, so the ratio's magnitude is at most 1.
            if abs(f1) > abs(f0):
                x = (-f0 / f1 * x1 + x0) / (1.0 - f0 / f1)
            else:
                x = (-f1 / f0 * x0 + x1) / (1.0 - f1 / f0)
            if abs(x - x1) <= state.xtol:
                return x
            x0, f0 = x1, f1
            x1, f1 = x, state.f(x)
            state.x_best = x1
