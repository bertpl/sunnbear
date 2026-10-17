"""`AndersonBjorck` implements the Anderson-Björck method: regula falsi that scales down a bound's function value."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound
from sunnbear._core.solvers.core.formulas import chord_zero

from .state import AndersonBjorckState


class AndersonBjorck(BracketingSolver[AndersonBjorckState]):
    """`AndersonBjorck` is regula falsi that scales down the function value of a bound kept twice in a row.

    Like regula falsi, `AndersonBjorck` evaluates the zero of the chord through ``(a, f(a))`` and ``(b, f(b))``.

    Regula falsi stalls when the function is convex or concave on the interval: regula falsi keeps 1 bound forever,
    so the interval never shrinks below the distance from that bound to the root.

    The Anderson-Björck method (Anderson and Björck, 1973) avoids the stall the way the Illinois method does: it scales
    down the function value of the bound that it keeps, by a factor:

        Illinois:          factor = 0.5
        Pegasus:           factor = f_previous / (f_previous + f_new)
        Anderson-Björck:   factor = 1 - f_new / f_previous, or 0.5 where that is not positive

    ``f_previous`` and ``f_new`` are the function values at the previous and the new iterate. They have the same sign
    whenever the factor applies, so ``1 - f_new / f_previous`` is below 1, and closer to 1 the more the new iterate
    reduced ``|f|``; it is not positive when the new iterate did not reduce ``|f|``.

    Each new iterate replaces 1 bound, and the other bound is the retained bound:

    - when a new iterate lies on the same side of the root as the previous iterate, the retained bound's function
      value is multiplied by the factor before the next chord is drawn, which moves the next iterate toward the
      retained bound;
    - each further iteration that keeps that bound multiplies its value again, by that iteration's factor;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, with its
      unscaled function value.

    `AndersonBjorck` computes the factor as the paper's ALGOL procedure does: as the ratio of 2 chord slopes, the slope
    from the previous to the new iterate divided by the slope of the chord that produced the new iterate. For a new
    iterate at that chord's zero, the ratio equals ``1 - f_new / f_previous`` in exact arithmetic.

    `AndersonBjorck` also takes the procedure's step of delta, with ``delta = xtol``: when the chord's zero lies within
    ``delta`` of the most recent iterate, it evaluates the x-value at exactly ``delta`` from that iterate, toward the
    retained bound.

    From a most recent iterate within ``delta`` of the root, that step crosses the root and leaves an interval
    ``delta`` wide, which ends the solve.

    On a function that is nearly flat on 1 side of the root, over a large interval, the method can make very slow
    progress, and can need more than 200 iterations.

    When 2 iterates in a row land on the flat side with nearly equal function values, the factor is close to 0, and
    the next iterate lies close to the retained bound, on the same side of the root, so that iterate replaces the
    retained bound but moves it only slightly.

    `AndersonBjorck` departs from the ALGOL procedure, or settles a detail that the procedure leaves to its caller, in
    these places:

    - **Stopping criterion:** `AndersonBjorck` stops by `BracketingSolver`'s criterion, where the procedure stops by
      its own:

      - `AndersonBjorck` stops once the interval is at most ``2*xtol`` wide or the function value at a bound is 0, and
        returns that bound, or else the interval's midpoint, which lies within ``xtol`` of a root;
      - the procedure stops once the interval is at most ``delta`` wide or the function value at the most recent
        iterate is 0, and returns whichever of the most recent iterate and the retained bound has the smaller ``|f|``,
        with the retained bound's ``|f|`` scaled.
    - **Tolerance ``delta``:** the procedure leaves ``delta`` to its caller, and uses it both as the length of a step
      of delta and as its stopping width. `AndersonBjorck` sets ``delta = xtol``, half the shared stopping width, so
      that a step of delta lands inside the interval while the solve continues. With ``delta`` equal to the stopping
      width, as in the procedure, the solve can alternate between 2 x-values until its evaluation budget runs out:
      once the interval is ``delta`` wide in exact arithmetic, its computed width can round to just above ``delta``,
      so the solve continues, and a step of delta from 1 bound lands on the other.
    - **Chord's zero:** `AndersonBjorck` computes it with `chord_zero`; the procedure computes it as ``x1 - f1 / w1``,
      a step from the most recent iterate ``x1``, where ``w1 = (f1 - f0) / (x1 - x0)`` is the slope of the chord
      through ``(x1, f1)`` and ``(x0, f0)``, with ``x0`` the retained bound and ``f0`` its scaled value; the 2 forms
      are equal in exact arithmetic but round differently.
    - **Side of the root:** the procedure tests whether a new iterate ``x2`` lies on the other side of the root by
      ``f2 * f1 <= 0``, with ``f2`` the function value at ``x2``; the product of 2 small function values can underflow
      to 0, so `AndersonBjorck` splits the interval by the sign of ``f2`` alone, with `Interval.split_at`.
    - **A chord's zero on the most recent iterate:** where ``xtol`` lies below half the float spacing at the most
      recent iterate, as at ``xtol = 0``, the step of delta does not move the chord's zero, which can then round onto
      that iterate, so that the slope between the chord's zero and that iterate is ``0 / 0``. `AndersonBjorck` then
      takes the factor 0.5, through a test ``x2 == x1`` that the procedure does not have; in IEEE arithmetic, the
      procedure's ``0 / 0`` is NaN, which fails its test that the factor is positive, so the procedure takes 0.5 too.
    - **Starting order:** the procedure leaves the order of its 2 starting x-values to the caller; `AndersonBjorck`
      passes the upper bound as ``x1``, the second of them, as the paper's examples and mpmath do.

    References:
        - Anderson, N. and Björck, Å. (1973). A new high order method of regula falsi type for computing a root of an
          equation. BIT 13(3), 253-264. Its equation 7 is the factor, its section 3 the fallback to 0.5, and its
          section 6 gives the ALGOL procedure, which holds the step of delta and the form of `AndersonBjorck`'s
          factor; the test suite reproduces the iteration counts of its Examples 1 to 7.
          https://doi.org/10.1007/BF01951936
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. Its equation 5, with ``gamma = f[x_(i+1), x_i] / f[x_i, x_(i-1)]`` from its Table 1,
          is the Anderson-Björck step, with ``gamma = 0.5`` as its fallback; its Table 4 shows the slow progress on
          large intervals, and the test suite reproduces that table.
        - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="anderson"``; the test suite checks
          `AndersonBjorck` against mpmath's ``Illinois``.
    """

    name = "anderson_bjorck"
    version = 5
    state_cls = AndersonBjorckState

    def _next_x(self, state: AndersonBjorckState, interval: Interval) -> float:
        """Return the chord's zero, or the step of delta in its place, as the class docstring says.

        Before computing the chord, update `AndersonBjorckState`'s own fields from the replaced bound; the new iterate
        is the previous call's return value. This update is correct only when exactly 1 new evaluation happened since
        the previous call.
        """
        # --- update the retained bound's value --
        # The names are the ALGOL procedure's: x2 is the new iterate, and x0 the retained bound; until the update
        # below, x1 is the previous iterate, and f0 the retained bound's scaled value.
        replaced_bound = interval.last_replaced_bound
        if replaced_bound is None:
            pass  # This is the first iteration: no bound has been kept again yet, so no value is scaled.
        else:
            if replaced_bound is IntervalBound.LOWER:
                x2, f2, x0 = interval.a, interval.fa, interval.b
            else:
                x2, f2, x0 = interval.b, interval.fb, interval.a
            x1, f1, f0 = state.newest_x, state.newest_f, state.scaled_retained_f
            if replaced_bound is not state.newest_bound:
                # x2 replaced the retained bound, on the other side of the root from x1, so x1 becomes the retained
                # bound, with its unscaled function value f1.
                state.scaled_retained_f = f1
                state.newest_bound = replaced_bound
            elif x2 == x1:
                # x2 equals x1, so the slope w2 = (f2 - f1) / (x2 - x1) would be 0 / 0, as the class docstring says.
                state.scaled_retained_f = 0.5 * f0
            else:
                # x2 replaced x1, so the retained bound x0 was kept once more.
                w1 = (f1 - f0) / (x1 - x0)
                w2 = (f2 - f1) / (x2 - x1)
                g1 = w2 / w1
                if g1 > 0.0:
                    state.scaled_retained_f = g1 * f0
                else:
                    # x2 did not reduce |f|, so the Illinois method's factor replaces g1.
                    state.scaled_retained_f = 0.5 * f0
            state.newest_x, state.newest_f = x2, f2

        # --- the paper's step -------------------
        if state.newest_bound is IntervalBound.UPPER:
            x0, x1, f1 = interval.a, interval.b, interval.fb
        else:
            x0, x1, f1 = interval.b, interval.a, interval.fa
        x2 = chord_zero(x0, state.scaled_retained_f, x1, f1)

        # --- the step of delta ------------------
        delta = state.xtol
        if abs(x2 - x1) < delta:
            # This is the procedure's x1 - delta*sign(x1 - x0), which steps delta from x1 toward the retained bound x0.
            if state.newest_bound is IntervalBound.UPPER:
                x2 = x1 - delta
            else:
                x2 = x1 + delta
        return x2
