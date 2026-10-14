"""`AndersonBjorck` implements the Anderson-Björck method: regula falsi that scales down a bound's function value.

The rest of this docstring is the record of `AndersonBjorck` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - Ia - article code: Anderson and Björck (1973), the ALGOL procedure in its section 6;
      - Ib - article pseudocode: none;
      - Ic - article text: Anderson and Björck (1973), its equations 2 and 5 to 7, the rule of its section 3 for a
        factor that is not positive, and its section 5, which states the starting x-values and the stopping rule of
        its examples.
    - II - authors' code:
      - none.
    - III - third party:
      - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="anderson"``;
      - Ford (1997), equation 5, with the factor of its Table 1;
      - the C# code ``AndersonBjork.cs`` in the supplementary material of Ganchovski et al. (2026).
    - IV - own judgment:
      - none.

Source per aspect:
    Every aspect follows the ALGOL procedure of Anderson and Björck (1973), except:
    - `AndersonBjorck` passes the upper bound as ``x1``, the second of the 2 starting x-values, as the article's
      Examples 1 to 7 and mpmath do, because the ALGOL procedure leaves the order of ``x0`` and ``x1`` to the caller.
      With the lower bound as ``x1``, 4 of the 15 counts of Ford's Table 4 change by 1.
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound, as for every
      solver. When the function value is 0 at the lower bound, the ALGOL procedure first evaluates the function at the
      zero of the chord through the 2 bounds, which lies at that bound up to rounding, and returns that bound after 1
      or 2 more evaluations.
    - The code leaves out the ALGOL procedure's step of delta, as mpmath and the C# code do. The step moves a chord's
      zero that lies within ``delta`` of the most recent iterate to exactly ``delta`` from it, and in float64 it can
      make the procedure alternate forever between the 2 interval bounds: a port with the step does not end on 11 of
      the 26 runs of the article's Examples 1 to 7 at ``delta = 6e-8``. Without the step, a chord's zero can round onto
      the most recent iterate.
    - Unlike the ALGOL procedure, the code tests ``x2 == x1``, with ``x2`` the chord's zero and ``x1`` the most recent
      iterate, and takes the factor 0.5 when ``x2 == x1``, because a chord's zero that rounds onto the most recent
      iterate makes the computation of the slope ``w2`` from ``x1`` to ``x2`` divide 0 by 0, which raises an error in
      Python. In IEEE arithmetic, the procedure's scaling factor ``g1`` is then NaN, which fails its test
      ``g1 > 0.0``, so the procedure takes 0.5 there too; the test ``x2 == x1`` costs 1 counted comparison per
      iteration that keeps the retained bound.
    - Translation of ``xtol`` (P7): ``xtol`` is the ALGOL procedure's ``delta``, which, without the step of delta,
      enters only the stopping test.

Validation:
    - A - authors' results:
      - TBD: Examples 1 to 7, the 26 iteration counts of the column "Alg. A". At ``xtol = 6e-8``, the article's
        ``delta``, 10 of the counts match, 11 differ by 1, and 5 differ by 2 or 3; the docstring of the test package
        ``tests.solvers.bracketing.anderson_bjorck`` gives the details.
      - PRINCIPLE-GAP (P5): P5 does not say whether a deviation that the solver declares counts as a stated cause of a
        difference from published results. The article ran Examples 1 to 7 with the step of delta, which
        `AndersonBjorck` leaves out, and in 27-bit arithmetic; a port of the ALGOL procedure that takes the step of
        delta, in emulated 27-bit arithmetic, brings the 5 counts that differ by 2 or 3 to within 1 of the article's,
        but does not end on 8 of the other 21 runs. No test checks the examples.
      - not used: the double-precision totals on p. 263, which `AndersonBjorck` does not reproduce at
        ``xtol = 6e-16``, for a cause that is not known: 133 iterations against 147 on Examples 1 to 5, and 60 against
        50 on Examples 6 and 7.
    - B - third-party results:
      - used: Ford (1997), Table 4, reproduced exactly, which is convincing (P5);
      - not used: the columns "AB" of Table 2 of Ganchovski et al. (2026) and of Ganchovski and Traykov (2023); the
        docstring of the test package ``tests.solvers.bracketing.anderson_bjorck`` gives the reasons.
    - C - reference implementation:
      - used: a twin test checks that `AndersonBjorck` evaluates the same x-values as mpmath's ``Illinois`` with
        ``method="anderson"``; the twin test imposes the stopping rule of `AndersonBjorck` on mpmath.

Variants:
    - `AndersonBjorckConfig`, the only config, is secondary (P8); this record marks no PRINCIPLE-CONFLICT.
"""

from sunnbear._core.solvers.core import Solver, SolveState


class AndersonBjorck(Solver):
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

    The chord's zero can round onto the most recent iterate, once that iterate lies within rounding error of the root
    while the retained bound is still far from it. The new iterate then equals the previous one in both x and f, so
    the slope between them is ``0 / 0``, and `AndersonBjorck` takes the factor 0.5.

    On a function that is nearly flat on 1 side of the root, over a large interval, the method can make very slow
    progress, and can need more than 200 iterations.

    When 2 iterates in a row land on the flat side with nearly equal function values, the factor is close to 0, and
    the next iterate lies close to the retained bound, on the same side of the root, so that iterate replaces the
    retained bound but moves it only slightly.

    `AndersonBjorck` stops by its paper's own criterion, so it writes its own loop, not `BracketingSolver`'s.

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
          `AndersonBjorck` against mpmath's ``Illinois``.
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its supplementary material holds the
          C# code ``AndersonBjork.cs``, an implementation of the Anderson-Björck method, and its Table 2 gives that
          code's evaluation counts in the column "AB". https://doi.org/10.3390/a19050332
        - The authors' repository of Ganchovski et al. (2026), https://github.com/Just-A-Random-Geek/ModAB-Root-Finding,
          which holds the paper's supplementary material, ``AndersonBjork.cs`` among it.
        - Ganchovski, N. and Traykov, A. (2023). Modified Anderson-Bjork's method for solving non-linear equations in
          structural mechanics. IOP Conference Series: Materials Science and Engineering 1276, 012010. Its Table 2
          holds the column "AB", for runs whose stopping rule the paper does not state.
          https://doi.org/10.1088/1757-899X/1276/1/012010
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
