"""`Secant` implements the secant method, which evaluates the zero of the line through the 2 latest iterates."""

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.exceptions import DivergedError


class Secant(Solver):
    """`Secant` implements the secant method, in the form of SciPy's ``scipy.optimize.newton`` without a derivative.

    Each iteration computes the zero of the secant, the line through ``(x0, f0)`` and ``(x1, f1)``, where ``x0`` and
    ``x1`` are the 2 latest x-values, ``x1`` the newest. Near a simple root, the method converges faster than
    linearly, with order about 1.618.

    `Secant` is an open method: it keeps no interval around the root, so its iterates may leave the initial
    interval, and its result is not guaranteed to lie within ``xtol`` of a root.

    A solve runs as follows:

    - **Starting x-values:** the bounds of the initial interval. The method treats one bound as the older x-value and
      the other as the newest x-value, and the newest x-value is the bound with the larger ``|f|``, or the upper bound
      when both are equal.
    - **Step formula:** the zero of the secant, computed from the ratio of the 2 function values, with the value of
      smaller magnitude divided by the value of larger magnitude, so that the ratio's magnitude is at most 1.
    - **Stopping criterion:** the solve ends once the step from the newest x-value to the next x-value is at most
      ``xtol``, and returns that next x-value without evaluating it.
    - **Equal function values:** when the 2 latest x-values have equal function values, the secant is horizontal and
      its zero lies at infinity. `Secant` then raises `DivergedError`, which `Solver.solve` records as ``DIVERGED``.
      This deviates from SciPy, which returns the midpoint of the 2 x-values, flagged as not converged, a result for
      which the framework has no status.

    A small step does not show that the next x-value is close to a root: on a function that is nearly flat between 2
    x-values, a step taken far from the root can be smaller than ``xtol``.

    `Secant` keeps no interval around the root, so it writes its own loop, not `BracketingSolver`'s.

    References:
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section 9.2.
          Cambridge University Press. Its ``rtsec`` takes the bound with the smaller ``|f|`` as the newest x-value,
          where SciPy and `Secant` take the bound with the larger ``|f|``.
        - SciPy's ``scipy.optimize.newton``, without a derivative; the test suite checks `Secant` against
          ``scipy.optimize.newton``.
        - Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition, section 2.3.
          John Wiley & Sons. Its error test for the secant method, the step between 2 successive iterates, is the
          stopping criterion of `Secant`.
        - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
          performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5. Its
          Table 1 holds the column "Secant", for a secant method that stops once the smaller ``|f|`` of its 2 latest
          x-values is at most 1e-10. https://doi.org/10.1145/3423597
    """

    name = "secant"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Run the secant method from the interval bounds; return the first secant zero within ``xtol`` of its start.

        Each iteration computes the zero of the secant through the 2 latest x-values. If the step from the newest
        x-value to that zero is at most ``xtol``, the iteration returns the zero; otherwise it evaluates the zero and
        makes that zero the newest x-value.

        Raises:
            DivergedError: If the 2 latest x-values have equal function values, so the next x-value lies at infinity.
        """
        # --- starting x-values ------------------
        # x0 and x1 are the 2 latest x-values, x1 the newest, with function values f0 and f1.
        interval = state.interval
        x0, x1, f0, f1 = interval.a, interval.b, interval.fa, interval.fb
        # The newest x-value is the bound with the larger |f|, the upper bound when both are equal, as in SciPy.
        if abs(f1) < abs(f0):
            x0, x1, f0, f1 = x1, x0, f1, f0
        state.x_best = x1

        # --- main loop --------------------------
        while True:
            if f1 == f0:
                raise DivergedError(
                    "The 2 latest x-values have equal function values, so the next x-value is infinite."
                )
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
