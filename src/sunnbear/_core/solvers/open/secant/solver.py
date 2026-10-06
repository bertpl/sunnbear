"""`Secant` implements the secant method: each step evaluates where the line through the 2 latest points is zero."""

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.exceptions import DivergedError


class Secant(Solver):
    """`Secant` implements the secant method, in the form of SciPy's ``scipy.optimize.newton`` without a derivative.

    Each step computes the zero of the line through the 2 latest points, the secant. Near a simple root, the method
    converges faster than linearly, with order about 1.618. It is an open method: it keeps no interval around the
    root, so its iterates may leave the initial interval, and its result is not guaranteed to lie within ``xtol`` of
    a root.

    `Secant` follows SciPy in 4 respects:

    - **Starting points:** the bounds of the initial interval. When the upper bound has the smaller ``|f|``, the 2
      are swapped, so the newest point is the one with the larger ``|f|``.
    - **Step formula:** the zero of the secant, with the smaller of the 2 function values divided by the larger, so
      that the ratio's magnitude is at most 1.
    - **Stopping criterion:** the solve ends once the step from the newest point to the next point is at most
      ``xtol``, and returns that next point without evaluating it.
    - **Equal function values:** when the 2 latest points have equal function values, the secant is horizontal and
      its zero lies at infinity. `Secant` then raises `DivergedError`, which `Solver.solve` records as ``DIVERGED``;
      SciPy returns the midpoint of the 2 points as a result that did not converge.

    A small step does not show that the next point is close to a root: on a function that is nearly flat between 2
    points, a step can be smaller than ``xtol`` far from the root.

    The loop keeps no interval, so `Secant` subclasses `Solver` and writes its own loop, not `BracketingSolver`'s.

    References:
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section 9.2.
          Cambridge University Press.
        - SciPy's ``scipy.optimize.newton``, without a derivative; the test suite checks `Secant` against it.
    """

    name = "secant"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Run the secant method from the interval bounds and return the first point whose step is at most ``xtol``.

        ``x0`` and ``x1`` are the 2 latest points, ``x1`` the newest, with function values ``f0`` and ``f1``.
        """
        # --- starting points ----------------------------
        interval = state.interval
        x0, x1, f0, f1 = interval.a, interval.b, interval.fa, interval.fb
        if abs(f1) < abs(f0):
            x0, x1, f0, f1 = x1, x0, f1, f0
        state.x_best = x1

        # --- main loop ----------------------------------
        while True:
            if f1 == f0:
                raise DivergedError("The 2 latest points have equal function values, so the next point is infinite.")
            if abs(f1) > abs(f0):
                x = (-f0 / f1 * x1 + x0) / (1.0 - f0 / f1)
            else:
                x = (-f1 / f0 * x0 + x1) / (1.0 - f1 / f0)
            if abs(x - x1) <= state.xtol:
                return x
            x0, f0 = x1, f1
            x1, f1 = x, state.f(x)
            state.x_best = x1
