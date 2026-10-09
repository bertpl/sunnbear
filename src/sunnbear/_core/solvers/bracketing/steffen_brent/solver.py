"""`SteffenBrent` implements the modified Brent method of Steffen et al., which can move a bound onto the midpoint."""

from sunnbear._core.solvers.core import Solver, SolveState


class SteffenBrent(Solver):
    """`SteffenBrent` implements the modified Brent method of Steffen et al. (2025), as the paper's Algorithm 2.

    The method keeps 2 interval bounds, ``a`` and ``b``, with ``b`` the one with the smaller ``|f|``, which is the
    best estimate. Each iteration evaluates a new x-value ``s``, from 1 of 3 steps:

    - inverse quadratic interpolation through ``a``, ``b`` and ``b_prev``, the previous value of ``b``, when the 3
      function values are distinct;
    - linear interpolation, a secant step, through ``b`` and ``b_prev``, when only their function values differ;
    - bisection, in all other cases, and in place of an interpolation step that does not land strictly between ``b``
      and ``(3 * a + b) / 4``.

    In the first iteration, ``b_prev`` is ``a``, so the first step is a secant step.

    ``s`` becomes the new ``b``, and the new ``a`` is chosen so that the interval keeps the root:

    - when ``f(a)`` and ``f(s)`` have the same sign, the old ``b`` becomes the new ``a``, as in Brent's method;
    - otherwise the root lies between ``a`` and ``s``, and the method evaluates the midpoint ``m = (a + b) / 2`` of
      the old interval; when ``f(m)`` and ``f(s)`` differ in sign, ``m`` becomes the new ``a``.

    The second case is the paper's modification of Brent's method. Finally, ``a`` and ``b`` swap where needed, so that
    ``b`` keeps the smaller ``|f|``.

    The solve ends once ``|b - a| <= xtol`` or ``f(b) = 0``, and returns ``b``, which then lies within ``xtol`` of a
    root. The paper stops once ``|b - a| <= tol1`` or ``|f(b)| <= tol2``; the solver passes ``xtol`` as ``tol1`` and
    0 as ``tol2``.

    Where the paper is ambiguous, `SteffenBrent` makes these choices:

    - **The interval for an accepted step:** the paper's text accepts an interpolation step only between ``b`` and
      the midpoint ``(a + b) / 2``, while its Algorithm 2 keeps the bound of Brent's method, ``(3 * a + b) / 4``.
      `SteffenBrent` follows Algorithm 2.
    - **The choice of step:** Algorithm 2 chooses between interpolation and the secant by comparing the x-values
      ``a``, ``b`` and ``b_prev``, not the function values. Its secant step then divides 0 by 0 when ``b`` equals
      ``b_prev``, which happens when the old ``b`` became the new ``a`` and the final swap moves it back to ``b``, and
      its interpolation divides by 0 when 2 distinct x-values share a function value. `SteffenBrent` compares the
      function values, for exact equality.
    - **No step-size tests:** the paper's text describes the tests of Brent's method that force bisection once the
      interpolation steps stop shrinking, but Algorithm 2 leaves them out. `SteffenBrent` follows Algorithm 2, so on
      some functions the interval shrinks slowly.
    - **No needless evaluation of the midpoint:** when ``s`` is itself the midpoint, its function value serves as
      ``f(m)``, where Algorithm 2 evaluates the midpoint a second time; and an ``s`` with ``f(s) = 0`` ends the
      solve without evaluating the midpoint. Neither shortcut changes the next interval or the returned x-value,
      since in both cases ``f(m)`` and ``f(s)`` cannot differ in sign.

    The paper's title says that the modification halves the interval in every iteration, but Algorithm 2 does not
    guarantee that the interval halves:

    - when the root lies between ``a`` and ``s``, and ``s`` lies on ``b``'s side of the midpoint, the midpoint test
      fails and the new interval runs from ``a`` to ``s``, more than half the old interval;
    - when ``f(a)`` and ``f(s)`` have the same sign, the new interval from ``b`` to ``s`` can keep up to 3/4 of the
      old interval.

    An iteration can evaluate the function twice, and the stopping criterion is the paper's own, so `SteffenBrent`
    writes its own loop, not `BracketingSolver`'s.

    References:
        - Steffen, V., Della Pasqua, C. C., de Oliveira, M. S. and da Silva, E. A. (2025). Halving interval
          guaranteed for Dekker and Brent root finding methods. Examples and Counterexamples 7, 100173. Its
          Algorithm 2 is the method, and the test suite reproduces its 2 case studies.
          https://doi.org/10.1016/j.exco.2024.100173
        - Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. The
          Computer Journal 14(4), 422-425. Steffen et al. modify Brent's method. https://doi.org/10.1093/comjnl/14.4.422
    """

    name = "steffen_brent"
    version = 1

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — the loop follows the paper's Algorithm 2 step by step
        """Run Algorithm 2 of the paper and return ``b``.

        Each iteration:

        - chooses ``s`` and evaluates it;
        - ends the solve if ``f(s) = 0``;
        - chooses the new ``a``, evaluating the midpoint where the paper's modification needs it;
        - swaps ``a`` and ``b`` where ``|f(a)| < |f(b)|``.

        The loop ends once ``|b - a| <= xtol``.
        """
        interval = state.interval
        a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb
        if abs(fa) < abs(fb):
            a, b, fa, fb = b, a, fb, fa
        b_prev, fb_prev = a, fa
        while abs(b - a) > state.xtol:
            m = (a + b) / 2.0

            # --- the step s ---------------------
            if fa != fb and fa != fb_prev and fb != fb_prev:
                # The step is an inverse quadratic interpolation through a, b and b_prev, the paper's equation 3.
                fb_over_fa = fb / fa
                fb_over_fb_prev = fb / fb_prev
                fa_over_fb_prev = fa / fb_prev
                numerator = fb_over_fa * (
                    (1.0 - fb_over_fb_prev) * (a - b)
                    + fa_over_fb_prev * (fb_over_fb_prev - fa_over_fb_prev) * (b_prev - b)
                )
                denominator = (fb_over_fb_prev - 1.0) * (fb_over_fa - 1.0) * (fa_over_fb_prev - 1.0)
                s = b + numerator / denominator
            elif fb != fb_prev:
                # The step is a linear interpolation through b and b_prev, the paper's equation 4.
                s = b - fb * (b_prev - b) / (fb_prev - fb)
            else:
                s = m
            # accepted_range_end is the end of the range that accepts an interpolation step. A step that overflows to
            # inf or nan falls outside the range too, so it becomes a bisection.
            accepted_range_end = (3.0 * a + b) / 4.0
            if not min(b, accepted_range_end) < s < max(b, accepted_range_end):
                s = m

            # --- the evaluation at s ------------
            fs = state.f(s)
            state.x_best = s
            if fs == 0.0:
                return s

            # --- the new interval ---------------
            b_prev, fb_prev = b, fb
            # Signs are compared directly, where the paper multiplies them: the product of 2 small function values can
            # underflow to 0.
            if (fa > 0.0) == (fs > 0.0):
                a, fa = b, fb
            elif s != m:
                fm = state.f(m)
                if (fm > 0.0 > fs) or (fm < 0.0 < fs):
                    # The root lies between m and s, so m replaces a: the paper's modification.
                    a, fa = m, fm
            b, fb = s, fs
            if abs(fa) < abs(fb):
                a, b, fa, fb = b, a, fb, fa
        return b
