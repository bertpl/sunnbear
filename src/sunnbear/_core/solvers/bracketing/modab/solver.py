"""`ModAB` implements the modified Anderson-Björck method, which switches between bisection and Anderson-Björck."""

from sunnbear._core.solvers.core import IntervalBound, Solver, SolveState

# With this factor, the Anderson-Björck steps may fall 4 steps behind bisection before the solve falls back to
# bisection: 16 = 2^4 (the paper's section 4.2).
_FALLBACK_THRESHOLD_FACTOR = 16.0


class ModAB(Solver):
    """`ModAB` ports the modified Anderson-Björck method of Ganchovski et al. (2026) from the paper's C# code.

    The method combines bisection with the Anderson-Björck method, the modified regula falsi method of `AndersonBjorck`.
    `ModAB` keeps the interval bounds ``x1 < x2`` with their function values ``y1`` and ``y2``, and runs in 1 of 2
    modes, starting with bisection:

    - **bisection:** the new x-value ``x3`` is the midpoint. After evaluating ``y3 = f(x3)``, the method switches to
      Anderson-Björck mode when the function looks close to a straight line on the interval:
      ``|ym - y3| < k * (|y3| + |ym|)``, where ``ym = (y1 + y2) / 2`` is the value of the chord at the midpoint,
      ``k = r^2``, and ``r = 1 - |ym / (y2 - y1)|`` measures how symmetric ``y1`` and ``y2`` are;
    - **Anderson-Björck:** ``x3`` is the zero of the chord, ``(x1 * y2 - y1 * x2) / (y2 - y1)``.

    ``x3`` replaces the bound whose function value has the sign of ``y3``.

    In Anderson-Björck mode, when the same bound stays fixed in 2 iterations in a row, its stored function value is
    multiplied by the factor of `AndersonBjorck`, ``m = 1 - y3 / y_moved``, where ``y_moved`` is the function value at
    the replaced bound; where ``m`` is not positive, the factor is 0.5.

    The switch to Anderson-Björck mode sets the threshold to `_FALLBACK_THRESHOLD_FACTOR` times the interval width,
    and every Anderson-Björck step halves the threshold; once the interval is wider than the threshold, the method falls
    back to bisection.

    The solve ends once ``y3 = 0``, or once the interval is at most ``aTol + rTol * |x3|`` wide, where ``aTol`` and
    ``rTol`` are the C# code's absolute and relative tolerances; in the second case, the solve returns ``x3`` without
    evaluating it.

    The solver passes ``xtol`` as ``aTol`` and 0 as ``rTol``; ``x3`` lies inside the interval, so it lies within
    ``xtol`` of a root.

    `ModAB` follows the C# code where the paper's Algorithm 1 differs from it or leaves a detail out:

    - **Clamping:** Algorithm 1 evaluates the chord's zero and then clamps it into the interval. The C# code clamps
      first: a chord's zero that rounding puts on or outside a bound is replaced by that bound and its stored function
      value, so nothing is evaluated. In Anderson-Björck mode, such an iteration only halves the stored function value
      at the other bound, or marks the other bound as fixed.
    - **The first threshold:** only the C# code shows the threshold's starting value at the switch.
    - **Scaled function values:** Anderson-Björck mode's scaled function values stay stored after a fallback to
      bisection, and the next bisection steps read them when they test whether the function looks close to a straight
      line.

    The C# code also stops after 200 iterations; `ModAB` leaves that limit out, so the solve's evaluation budget ends
    the solve.

    The method's first version (Ganchovski and Traykov, 2023) is a different algorithm, which the 2026 paper replaces;
    `ModAB` implements only the 2026 version. The first version differs in 3 ways:

    - it fixes ``k = 0.25``;
    - it falls back to bisection after a fixed number of iterations;
    - it stops once 2 successive x-values lie within the tolerance.

    `ModAB` stops by its own criterion, and returns an x-value that it has not evaluated, so it writes its own loop,
    not `BracketingSolver`'s.

    References:
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its Table A1 holds the C# code that
          `ModAB` ports, and the test suite reproduces its Tables 1 and 2. https://doi.org/10.3390/a19050332
        - Ganchovski, N. and Traykov, A. (2023). Modified Anderson-Björck's method for solving non-linear equations in
          structural mechanics. IOP Conference Series: Materials Science and Engineering 1276, 012010. The method's
          first version. https://doi.org/10.1088/1757-899X/1276/1/012010
    """

    name = "modab"
    version = 1

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — the loop follows the authors' C# code step by step
        """Run the loop of the paper's C# code and return the last ``x3``.

        The variables keep the names of the C# code, except for those listed below; the C# code also groups ``x1``
        and ``y1`` into the point ``p1``, and likewise ``p2`` and ``p3``.

        - ``x_new`` and ``y_new`` are the point that replaces a bound: ``x3`` and ``y3``, or, when ``x3`` is clamped
          onto a bound, that bound with its stored function value;
        - ``fixed_bound`` is the bound that stayed fixed in the last Anderson-Björck step, ``None`` before the first;
          the C# code stores it as the integer ``side``, although the comment on ``side`` calls it the side that moved
          last;
        - ``is_bisecting`` is the mode, ``bisection`` in the C# code.

        Each iteration:

        - computes ``x3``, and ends the solve if the interval is narrow enough;
        - evaluates ``x3``, unless it is clamped, and in bisection mode tests whether to switch;
        - ends the solve if ``y_new = 0``;
        - replaces a bound by ``(x_new, y_new)``, scaling the fixed bound's function value in Anderson-Björck mode;
        - falls back to bisection if the interval is wider than the threshold.
        """
        interval = state.interval
        x1, y1, x2, y2 = interval.a, interval.fa, interval.b, interval.fb
        is_bisecting = True
        fixed_bound: IntervalBound | None = None
        threshold = x2 - x1
        while True:
            # --- the new x-value x3 -------------
            if is_bisecting:
                x3 = (x1 + x2) / 2.0
            else:
                x3 = (x1 * y2 - y1 * x2) / (y2 - y1)
            if x2 - x1 <= self._get_stop_width(state.xtol, x3):
                return x3

            # --- the evaluation at x3 -----------
            if is_bisecting:
                y3 = state.f(x3)
                state.x_best = x3
                x_new, y_new = x3, y3
                ym = 0.5 * (y1 + y2)
                r = 1.0 - abs(ym / (y2 - y1))
                k = r * r
                if abs(ym - y3) < k * (abs(y3) + abs(ym)):
                    # The function is close enough to a straight line: switch to Anderson-Björck mode.
                    is_bisecting = False
                    threshold = (x2 - x1) * _FALLBACK_THRESHOLD_FACTOR
            else:
                if x3 <= x1:
                    x_new, y_new = x1, y1
                elif x3 >= x2:
                    x_new, y_new = x2, y2
                else:
                    y3 = state.f(x3)
                    state.x_best = x3
                    x_new, y_new = x3, y3
                threshold = threshold * 0.5
            if y_new == 0.0:
                return x3

            # --- the new interval ---------------
            # The C# code compares Math.Sign(y_new) with Math.Sign(y1); the test below gives the same result because
            # y_new is not 0 here.
            if (y_new > 0.0 and y1 > 0.0) or (y_new < 0.0 and y1 < 0.0):
                if fixed_bound is IntervalBound.UPPER:
                    m = 1.0 - y_new / y1
                    y2 = y2 * (0.5 if m <= 0.0 else m)
                elif not is_bisecting:
                    fixed_bound = IntervalBound.UPPER
                x1, y1 = x_new, y_new
            else:
                if fixed_bound is IntervalBound.LOWER:
                    m = 1.0 - y_new / y2
                    y1 = y1 * (0.5 if m <= 0.0 else m)
                elif not is_bisecting:
                    fixed_bound = IntervalBound.LOWER
                x2, y2 = x_new, y_new
            if x2 - x1 > threshold:
                # The Anderson-Björck steps shrink the interval too slowly: fall back to bisection.
                is_bisecting = True
                fixed_bound = None

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _get_stop_width(xtol: float, x3: float) -> float:
        """Return the interval width at or below which the solve stops.

        The C# code stops at ``aTol + rTol * |x3|``; `ModAB` passes ``xtol`` as ``aTol`` and 0 as ``rTol``, so
        `_get_stop_width` ignores ``x3``; a subclass that overrides this method can use ``x3`` for a relative tolerance.
        """
        return xtol
