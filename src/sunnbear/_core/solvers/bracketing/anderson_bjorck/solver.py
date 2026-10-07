"""`AndersonBjorck` implements the Anderson-Björck method: regula falsi that scales down a bound's function value."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound

from .state import AndersonBjorckState


class AndersonBjorck(BracketingSolver[AndersonBjorckState]):
    """`AndersonBjorck` is regula falsi that scales down the function value of a bound kept twice in a row.

    Like regula falsi, `AndersonBjorck` evaluates where the chord through the points at both bounds crosses zero.

    Regula falsi stalls when the function is convex or concave on the interval: regula falsi keeps 1 bound forever,
    so the interval never shrinks below the distance from that bound to the root.

    The Anderson-Björck method (Anderson and Björck, 1973) avoids the stall the way the Illinois method does: it scales
    down the function value of the bound that it keeps, but by a different factor.

    Each new iterate replaces 1 bound, and the other bound is the retained bound:

    - when a new iterate lies on the same side of the root as the previous iterate, the retained bound's function
      value is multiplied by ``1 - f_new / f_previous`` before the next chord is drawn, which moves the next iterate
      toward the retained bound:

      - ``f_previous`` and ``f_new`` are the function values at the previous and the new iterate; they have the same
        sign, so the factor is below 1, and closer to 1 the more the new iterate reduced ``|f|``;
      - when the new iterate did not reduce ``|f|``, the factor is not positive, and the Illinois method's factor,
        0.5, replaces it;
    - each further iteration that keeps that bound multiplies its value again, by that iteration's factor;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, with its
      unscaled function value.

    The factor is the ratio of 2 chord slopes: the slope from the previous to the new iterate, divided by the slope of
    the chord that produced the new iterate.

    The paper and Ford (1997) write the factor as this ratio of slopes. In exact arithmetic, the ratio equals
    ``1 - f_new / f_previous``, and `AndersonBjorck` computes the factor as ``1 - f_new / f_previous``, as mpmath's
    implementation does.

    The paper's algorithm adds 2 parts that `AndersonBjorck` leaves out, as mpmath does:

    - **a step of delta:** when the next point lies within ``delta`` of the newest point, the paper moves it to
      exactly ``delta`` from the newest point, toward the retained bound;
    - **its stopping criterion:** the paper stops once the interval is narrower than ``delta``, and returns the bound
      with the smaller ``|f|``.

    `AndersonBjorck` stops by the criterion of `BracketingSolver`, as `Illinois` and `Pegasus` do, so that the 3
    methods differ only in the factor.

    Ford (1997) states the Anderson-Björck step with regula falsi's chord formula, so the Anderson-Björck method
    differs from `RegulaFalsi` only in its function value at the retained bound, and from `Illinois` and `Pegasus`
    only in the factor.

    On a function that is nearly flat on 1 side of the root, over a large interval, the method can make very slow
    progress, and can need more than 200 iterations.

    When 2 iterates in a row land on the flat side with nearly equal function values, the factor is close to 0, and
    the next iterate lies close to the retained bound, on the same side of the root, so that iterate replaces the
    retained bound but moves it only slightly.

    References:
        - Anderson, N. and Björck, Å. (1973). A new high order method of regula falsi type for computing a root of an
          equation. BIT 13(3), 253-264. Its equation 7 is the factor, its section 3 the fallback to 0.5, and its
          section 6 the ALGOL procedure with the step of delta. https://doi.org/10.1007/BF01951936
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
    version = 1
    state_cls = AndersonBjorckState

    def _next_x(self, state: AndersonBjorckState, interval: Interval) -> float:
        """Return where the chord crosses zero, with the retained bound's value scaled as the class docstring says.

        Before computing the chord, update `AndersonBjorckState`'s own fields from the new iterate, which is the
        previous call's return value and now sits at the bound that it replaced. This update is correct only when
        exactly 1 new evaluation happened since the previous call.
        """
        # --- update the retained bound's value --
        # Until the update below, state.newest_bound and state.newest_f still describe the previous iterate.
        replaced_bound = interval.last_replaced_bound
        if replaced_bound is None:
            pass  # This is the first iteration: no bound has been kept again yet, so no value is scaled.
        else:
            new_iterate_f = interval.fa if replaced_bound is IntervalBound.LOWER else interval.fb
            if replaced_bound is state.newest_bound:
                # The new iterate replaced the previous iterate, so the retained bound was kept once more.
                previous_iterate_f = state.newest_f
                scaling_factor = 1.0 - new_iterate_f / previous_iterate_f
                if scaling_factor <= 0.0:
                    # The new iterate did not reduce |f|, so the Illinois method's factor replaces this one.
                    scaling_factor = 0.5
                state.scaled_retained_f = scaling_factor * state.scaled_retained_f
            else:
                # The new iterate replaced the retained bound, so the previous iterate is the retained bound now.
                state.scaled_retained_f = state.newest_f
                state.newest_bound = replaced_bound
            state.newest_f = new_iterate_f

        # --- regula falsi's chord ---------------
        if state.newest_bound is IntervalBound.UPPER:
            fa, fb = state.scaled_retained_f, interval.fb
        else:
            fa, fb = interval.fa, state.scaled_retained_f
        return (interval.a * fb - interval.b * fa) / (fb - fa)
