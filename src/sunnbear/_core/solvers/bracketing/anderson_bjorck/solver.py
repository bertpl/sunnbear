"""`AndersonBjorck` implements the Anderson-Björck method: regula falsi that scales down a bound's function value."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound

from .state import AndersonBjorckState


class AndersonBjorck(BracketingSolver[AndersonBjorckState]):
    """`AndersonBjorck` is regula falsi that scales down the function value of a bound kept twice in a row.

    Like regula falsi, `AndersonBjorck` evaluates where the chord through the points at both bounds crosses zero.

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

    `AndersonBjorck` computes the chord's zero and the factor as the paper's ALGOL procedure does:

    - **the chord's zero:** a step from the most recent iterate ``x1``, ``x1 - f1 / w1``, where ``w1 = (f1 - f0) /
      (x1 - x0)`` is the slope of the chord through ``(x1, f1)`` and ``(x0, f0)``, with ``x0`` the retained bound and
      ``f0`` its scaled value. In exact arithmetic, this is the x-value of regula falsi's chord formula, which
      `RegulaFalsi` computes as ``(a * fb - b * fa) / (fb - fa)``;
    - **the factor:** the ratio of 2 chord slopes, the slope from the previous to the new iterate divided by ``w1``,
      the slope of the chord that produced the new iterate. In exact arithmetic, the ratio equals
      ``1 - f_new / f_previous``.

    The paper's algorithm adds 2 parts that `AndersonBjorck` leaves out, as mpmath does:

    - **a step of delta:** when the next point lies within ``delta`` of the newest point, the paper moves it to
      exactly ``delta`` from the newest point, toward the retained bound;
    - **its stopping criterion:** the paper stops once the interval is narrower than ``delta``, and returns the bound
      with the smaller ``|f|``.

    Without the step of delta, the chord's zero can round onto the most recent iterate, once that iterate lies within
    rounding error of the root while the retained bound is still far from it.

    The slope from the previous to the new iterate is then ``0 / 0``, and `AndersonBjorck` takes the factor 0.5: in
    IEEE arithmetic, ``0 / 0`` is NaN, which fails the ALGOL procedure's test that the factor is positive, so the
    procedure takes 0.5 there too.

    `AndersonBjorck` stops by the criterion of `BracketingSolver`, as `Illinois` and `Pegasus` do, so that the
    benchmark compares the 3 methods under the same stopping criterion.

    On a function that is nearly flat on 1 side of the root, over a large interval, the method can make very slow
    progress, and can need more than 200 iterations.

    When 2 iterates in a row land on the flat side with nearly equal function values, the factor is close to 0, and
    the next iterate lies close to the retained bound, on the same side of the root, so that iterate replaces the
    retained bound but moves it only slightly.

    References:
        - Anderson, N. and Björck, Å. (1973). A new high order method of regula falsi type for computing a root of an
          equation. BIT 13(3), 253-264. Its equation 7 is the factor, its section 3 the fallback to 0.5, and its
          section 6 gives the ALGOL procedure, which holds the step of delta and the forms of the chord's zero and of
          the factor that `AndersonBjorck` computes. https://doi.org/10.1007/BF01951936
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. The paper covers the Anderson-Björck method in 3 places:

          - its equation 5, with ``gamma = f[x_(i+1), x_i] / f[x_i, x_(i-1)]`` from its Table 1, is the Anderson-Björck
            step;
          - the paper gives ``gamma = 0.5`` as the fallback factor;
          - its Table 4 shows the slow progress on large intervals.
        - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="anderson"``; the test suite checks
          `AndersonBjorck` against it.
    """

    name = "anderson_bjorck"
    version = 2
    state_cls = AndersonBjorckState

    def _next_x(self, state: AndersonBjorckState, interval: Interval) -> float:
        """Return where the chord crosses zero, with the retained bound's value scaled as the class docstring says.

        Before computing the chord, update `AndersonBjorckState`'s own fields from the new iterate, which is the
        previous call's return value and now sits at the bound that it replaced. This update is correct only when
        exactly 1 new evaluation happened since the previous call.
        """
        # --- update the retained bound's value --
        # Until the update below, the state's newest_* fields still describe the previous iterate.
        replaced_bound = interval.last_replaced_bound
        if replaced_bound is None:
            pass  # This is the first iteration: no bound has been kept again yet, so no value is scaled.
        else:
            if replaced_bound is IntervalBound.LOWER:
                new_iterate_x, new_iterate_f = interval.a, interval.fa
            else:
                new_iterate_x, new_iterate_f = interval.b, interval.fb
            if replaced_bound is state.newest_bound:
                # The new iterate replaced the previous iterate, so the retained bound was kept once more. The ALGOL
                # procedure's factor g1 is w2 / w1: its w2 is slope_between_iterates below, the slope from the previous
                # to the new iterate, and its w1 is state.chord_slope, the slope of the chord that produced the new
                # iterate.
                if new_iterate_x == state.newest_x:
                    # The step rounded onto the previous iterate, so w2 is 0 / 0, as the class docstring says.
                    scaling_factor = 0.5
                else:
                    slope_between_iterates = (new_iterate_f - state.newest_f) / (new_iterate_x - state.newest_x)
                    scaling_factor = slope_between_iterates / state.chord_slope
                    if scaling_factor <= 0.0:
                        # The new iterate did not reduce |f|, so the Illinois method's factor replaces this one.
                        scaling_factor = 0.5
                state.scaled_retained_f = scaling_factor * state.scaled_retained_f
            else:
                # The new iterate replaced the retained bound, so the previous iterate is the retained bound now.
                state.scaled_retained_f = state.newest_f
                state.newest_bound = replaced_bound
            state.newest_x, state.newest_f = new_iterate_x, new_iterate_f

        # --- the paper's step -------------------
        # The ALGOL procedure's w1, stored as state.chord_slope, is the slope of the chord through the most recent
        # iterate and the retained bound.
        retained_x = interval.a if state.newest_bound is IntervalBound.UPPER else interval.b
        state.chord_slope = (state.newest_f - state.scaled_retained_f) / (state.newest_x - retained_x)
        return state.newest_x - state.newest_f / state.chord_slope
