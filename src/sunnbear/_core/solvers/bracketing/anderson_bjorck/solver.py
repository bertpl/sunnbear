"""`AndersonBjorck` implements the Anderson-Björck method: regula falsi that scales down a bound's function value."""

from sunnbear._core.solvers.core import Solver, SolveState


class AndersonBjorck(Solver):
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

    - **the chord's zero:** ``x1 - f1 / w1``, a step from the most recent iterate ``x1``, where ``w1 = (f1 - f0) /
      (x1 - x0)`` is the slope of the chord through ``(x1, f1)`` and ``(x0, f0)``, with ``x0`` the retained bound and
      ``f0`` its scaled value. In exact arithmetic, this is the x-value of the chord formula that `RegulaFalsi`
      computes;
    - **the factor:** the ratio of 2 chord slopes, the slope from the previous to the new iterate divided by ``w1``,
      the slope of the chord that produced the new iterate. In exact arithmetic, the ratio equals
      ``1 - f_new / f_previous``.

    As for the chord's zero and the factor, `AndersonBjorck` follows its paper in its stopping rule, so that the
    benchmark measures the method as published. It stops as the ALGOL procedure does, with the procedure's tolerance
    ``delta`` set to ``xtol``:

    - **when it stops:** once the interval is at most ``xtol`` wide, or the function value at the most recent iterate
      is 0;
    - **what it returns:** the interval bound with the smaller ``|f|``, comparing the most recent iterate's ``|f1|``
      with the retained bound's scaled ``|f0|``, as the procedure does. The returned bound lies within ``xtol`` of a
      root.

    `Illinois` and `Pegasus` stop by the criterion of `BracketingSolver` instead, so in the benchmark `AndersonBjorck`
    uses a different stopping rule from the other 2 methods.

    Where the ALGOL procedure tests whether a new iterate ``x2`` lies on the other side of the root by
    ``f2 * f1 <= 0``, with ``f2`` the function value at ``x2``, `AndersonBjorck` compares the signs of ``f2`` and
    ``f1``, because the product of 2 small function values can underflow to 0.

    The ALGOL procedure also takes a step of delta, which `AndersonBjorck` leaves out: when the chord's zero lies within
    ``delta`` of the most recent iterate, the procedure moves the chord's zero to exactly ``delta`` from that iterate,
    toward the retained bound.

    `AndersonBjorck` leaves the step out because, in float64, it can make the procedure alternate forever between the
    2 bounds: once the interval is ``delta`` wide in exact arithmetic, its computed width ``|x1 - x0|`` can round to
    just above ``delta``, so the procedure does not stop; each step of delta then moves ``delta`` from the most recent
    iterate toward the retained bound, and so lands exactly on the retained bound.

    Without the step of delta, the chord's zero can round onto the most recent iterate, once that iterate lies within
    rounding error of the root while the retained bound is still far from it.

    When the chord's zero rounds onto the most recent iterate, the new iterate equals the previous one in both x and f,
    so the slope between them is ``0 / 0``. `AndersonBjorck` then takes the factor 0.5: in IEEE arithmetic, ``0 / 0``
    is NaN, which fails the ALGOL procedure's test that the factor is positive, so the procedure takes 0.5 there too.

    On a function that is nearly flat on 1 side of the root, over a large interval, the method can make very slow
    progress, and can need more than 200 iterations.

    When 2 iterates in a row land on the flat side with nearly equal function values, the factor is close to 0, and
    the next iterate lies close to the retained bound, on the same side of the root, so that iterate replaces the
    retained bound but moves it only slightly.

    References:
        - Anderson, N. and Björck, Å. (1973). A new high order method of regula falsi type for computing a root of an
          equation. BIT 13(3), 253-264. Its equation 7 is the factor, its section 3 the fallback to 0.5, and its
          section 6 gives the ALGOL procedure, which holds the step of delta, the stopping rule, and the forms of the
          chord's zero and of the factor that `AndersonBjorck` computes. https://doi.org/10.1007/BF01951936
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. The paper covers the Anderson-Björck method in 3 places:

          - its equation 5, with ``gamma = f[x_(i+1), x_i] / f[x_i, x_(i-1)]`` from its Table 1, is the Anderson-Björck
            step;
          - the paper gives ``gamma = 0.5`` as the fallback factor;
          - its Table 4 shows the slow progress on large intervals; the test suite reproduces that table.
        - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="anderson"``; the test suite checks
          `AndersonBjorck` against it.
    """

    name = "anderson_bjorck"
    version = 3

    def _solve(self, state: SolveState) -> float:
        """Run the loop of the paper's ALGOL procedure, without its step of delta, and return its root estimate.

        The variables keep the names of the ALGOL procedure, so that the code can be compared with the procedure line
        by line:

        - ``x1`` is the most recent iterate and ``f1`` its function value; before the first iterate, the upper bound
          counts as the most recent iterate;
        - ``x0`` is the retained bound and ``f0`` its scaled function value;
        - ``w1`` is the slope of the chord through ``(x0, f0)`` and ``(x1, f1)``, ``x2`` its zero and ``f2`` the
          function value there;
        - ``w2`` is the slope from ``x1`` to ``x2``, and ``g1 = w2 / w1`` the factor.

        Each iteration evaluates the chord's zero ``x2``, makes it the most recent iterate, and updates the retained
        bound as the class docstring says. The loop ends once the interval is at most ``xtol`` wide or ``f1`` is 0,
        and returns ``x1`` if ``|f1| < |f0|``, else ``x0``.
        """
        interval = state.interval
        x0, f0, x1, f1 = interval.a, interval.fa, interval.b, interval.fb
        while abs(x1 - x0) > state.xtol and f1 != 0.0:
            # --- the paper's step ---------------
            w1 = (f1 - f0) / (x1 - x0)
            x2 = x1 - f1 / w1
            f2 = state.f(x2)
            state.x_best = x2

            # --- update the retained bound ------
            # The ALGOL procedure tests f2 * f1 <= 0; the class docstring says why the signs are compared instead.
            if f2 == 0.0 or (f2 < 0.0) != (f1 < 0.0):
                # x2 lies on the other side of the root, so x1 becomes the retained bound, with its unscaled function
                # value f1.
                x0, f0 = x1, f1
            elif x2 == x1:
                # The step rounded onto the most recent iterate, so w2 is 0 / 0, as the class docstring says.
                f0 = 0.5 * f0
            else:
                w2 = (f2 - f1) / (x2 - x1)
                g1 = w2 / w1
                if g1 > 0.0:
                    f0 = g1 * f0
                else:
                    # x2 did not reduce |f|, so the Illinois method's factor replaces g1.
                    f0 = 0.5 * f0
            x1, f1 = x2, f2

        # --- the root estimate ------------------
        if abs(f1) < abs(f0):
            return x1
        else:
            return x0
