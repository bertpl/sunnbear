"""`SteffenBrent` implements the modified Brent method of Steffen et al., which can move a bound onto the midpoint."""

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.formulas import chord_zero, midpoint
from sunnbear._core.solvers.core.stopping import interval_root, is_interval_converged


class SteffenBrent(Solver):
    """`SteffenBrent` implements the modified Brent method of Steffen et al. (2025), as the paper's Algorithm 2.

    `SteffenBrent` keeps 2 interval bounds, ``a`` and ``b``; ``b`` is the bound with the smaller ``|f|``. Each
    iteration evaluates a new x-value ``s``, from 1 of 3 steps:

    - inverse quadratic interpolation through ``a``, ``b`` and ``b_previous``, the previous value of ``b``, when the 3
      function values are distinct;
    - linear interpolation, a secant step, through ``b`` and ``b_previous``, when the 3 function values are not
      distinct but ``f(b)`` and ``f(b_previous)`` differ;
    - bisection, in all other cases, and in place of an interpolation step that does not land strictly between ``b``
      and ``(3*a + b) / 4``.

    In the first iteration, ``b_previous`` is ``a``, so the first step is a secant step.

    ``s`` becomes the new ``b``, and the new ``a`` is chosen so that the interval keeps the root:

    - when ``f(a)`` and ``f(s)`` have the same sign, the old ``b`` becomes the new ``a``, as in Brent's method;
    - otherwise, ``f(s) = 0`` included, the root lies between ``a`` and ``s``, and `SteffenBrent` evaluates their
      midpoint ``m = (a + s) / 2``; when ``f(m)`` and ``f(s)`` differ in sign, ``m`` becomes the new ``a``.

    The second case is the paper's modification of Brent's method. Finally, ``a`` and ``b`` swap where needed, so that
    ``b`` keeps the smaller ``|f|``.

    The paper's title says that the modification halves the interval in every iteration, but Algorithm 2 does not
    guarantee that the interval halves:

    - when the root lies between ``a`` and ``m``, ``f(m)`` has the sign of ``f(s)``, so ``m`` does not replace ``a``,
      and the new interval runs from ``a`` to ``s``, more than half the old interval when ``s`` lies on ``b``'s side
      of ``(a + b) / 2``;
    - when ``f(a)`` and ``f(s)`` have the same sign, the new interval from ``b`` to ``s`` can keep up to 3/4 of the
      old interval.

    `SteffenBrent` departs from Algorithm 2, or settles a detail where the paper is ambiguous, in these places:

    - **Stopping criterion:** `SteffenBrent` checks the shared stopping criterion where Algorithm 2 checks its own, at
      the top of each iteration:

      - the solve ends once the interval is at most ``2*xtol`` wide, or once the function value at an interval bound
        is exactly 0, and returns that bound, or else the interval's midpoint, which then lies within ``xtol`` of a
        root;
      - Algorithm 2 ends the solve once ``|b - a| <= tol1`` or ``|f(b)| <= tol2``, and returns ``b``.
    - **Midpoint of the modification:** the paper's text and Algorithm 2 take ``m = (a + b) / 2``, the midpoint of the
      interval before the step, but the paper's results follow ``m = (a + s) / 2``: only that midpoint reproduces the
      values of the modified method in the paper's Figures 3, 4, 6 and 7. `SteffenBrent` follows the paper's results.
    - **Interval for an accepted step:** the paper's text accepts an interpolation step only between ``b`` and the
      midpoint ``(a + b) / 2``, while Algorithm 2 keeps the bound of Brent's method, ``(3*a + b) / 4``. `SteffenBrent`
      follows Algorithm 2.
    - **No step-size tests:** the paper's text describes the tests of Brent's method that force bisection once the
      interpolation steps stop shrinking, but Algorithm 2 leaves them out. `SteffenBrent` follows Algorithm 2, so on
      some functions the interval shrinks slowly.
    - **Choice of step:** `SteffenBrent` chooses the step by testing the function values for exact equality, where
      Algorithm 2 compares the x-values ``a``, ``b`` and ``b_previous``. Comparing the x-values leads to 2 divisions
      by 0:

      - the secant step divides 0 by 0 when ``b`` equals ``b_previous``, which happens when the old ``b`` became the
        new ``a`` and the final swap moves the old ``b`` back to ``b``;
      - the interpolation divides by 0 when 2 distinct x-values share a function value.
    - **Secant step:** `SteffenBrent` computes it with `chord_zero`; the paper's equation 4 steps from ``b`` instead,
      as ``b - f(b)*(b_previous - b) / (f(b_previous) - f(b))``, which is equal in exact arithmetic but rounds
      differently.
    - **Sign tests:** `SteffenBrent` compares the signs of 2 function values directly, where Algorithm 2 multiplies
      them: the product of 2 small function values can underflow to 0.

    An iteration can evaluate the function twice, and its steps read ``b_previous`` besides the 2 interval bounds, so
    `SteffenBrent` writes its own loop, not `BracketingSolver`'s.

    References:
        - Steffen, V., Della Pasqua, C. C., de Oliveira, M. S. and da Silva, E. A. (2025). Halving interval
          guaranteed for Dekker and Brent root finding methods. Examples and Counterexamples 7, 100173. Its
          Algorithm 2 is the method, and the test suite reproduces its 2 case studies and the modified Brent method's
          values in its Figures 3, 4, 6 and 7. https://doi.org/10.1016/j.exco.2024.100173
        - Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. The
          Computer Journal 14(4), 422-425. Steffen et al. modify Brent's method. https://doi.org/10.1093/comjnl/14.4.422
        - rateslib's ``_brent``, which rateslib's function ``ift_1dim`` runs for the method ``modified_brent``, is an
          implementation of Algorithm 2 that also chooses the step by testing the function values.
          https://github.com/attack68/rateslib
    """

    name = "steffen_brent"
    version = 4

    def _solve(self, state: SolveState) -> float:
        """Run Algorithm 2 of the paper until `_root_if_converged` returns a root estimate, and return that estimate.

        Each iteration:

        - ends the solve if the stopping criterion holds;
        - chooses ``s`` and evaluates it;
        - chooses the new ``a``, evaluating the midpoint of ``a`` and ``s`` where the paper's modification needs it;
        - swaps ``a`` and ``b`` where ``|f(a)| < |f(b)|``.
        """
        interval = state.interval
        a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb
        xtol_doubled = 2.0 * state.xtol
        if abs(fa) < abs(fb):
            a, b, fa, fb = b, a, fb, fa
        b_previous, fb_previous = a, fa
        while True:
            # --- the stopping criterion ---------
            x_root = self._root_if_converged(a, fa, b, fb, xtol_doubled)
            if x_root is not None:
                return x_root

            # --- the step s ---------------------
            if fa != fb and fa != fb_previous and fb != fb_previous:
                # The step is an inverse quadratic interpolation through a, b and b_previous, the paper's equation 3.
                fb_over_fa = fb / fa
                fb_over_fb_previous = fb / fb_previous
                fa_over_fb_previous = fa / fb_previous
                numerator = fb_over_fa * (
                    (1.0 - fb_over_fb_previous) * (a - b)
                    + fa_over_fb_previous * (fb_over_fb_previous - fa_over_fb_previous) * (b_previous - b)
                )
                denominator = (fb_over_fb_previous - 1.0) * (fb_over_fa - 1.0) * (fa_over_fb_previous - 1.0)
                s = b + numerator / denominator
            elif fb != fb_previous:
                # The step is the paper's equation 4: the zero of the chord through b and b_previous.
                s = chord_zero(b, fb, b_previous, fb_previous)
            else:
                s = midpoint(a, b)
            # An interpolation step that overflows to inf or nan fails this comparison too, so it becomes a bisection.
            accepted_range_end = (3.0 * a + b) / 4.0
            if not min(b, accepted_range_end) < s < max(b, accepted_range_end):
                s = midpoint(a, b)

            # --- the evaluation at s ------------
            fs = state.f(s)
            state.x_best = s

            # --- the new interval ---------------
            b_previous, fb_previous = b, fb
            # Signs are compared directly, where Algorithm 2 multiplies them, because the product of 2 small function
            # values can underflow to 0. Each test holds exactly where Algorithm 2's product is positive or negative,
            # so f(s) = 0 takes the else branch, as in Algorithm 2.
            if (fa > 0.0 and fs > 0.0) or (fa < 0.0 and fs < 0.0):
                a, fa = b, fb
            else:
                m = midpoint(a, s)
                fm = state.f(m)
                if (fm > 0.0 > fs) or (fm < 0.0 < fs):
                    # The root lies between m and s, so m replaces a: the paper's modification.
                    a, fa = m, fm
            b, fb = s, fs
            if abs(fa) < abs(fb):
                a, b, fa, fb = b, a, fb, fa

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _root_if_converged(a: float, fa: float, b: float, fb: float, xtol_doubled: float) -> float | None:
        """Return the root estimate if the solve ends at these interval bounds, or ``None`` if it continues.

        The test suite overrides this method to apply Algorithm 2's own stopping criterion where it reproduces the
        paper's published results.
        """
        if is_interval_converged(a, fa, b, fb, xtol_doubled):
            return interval_root(a, fa, b, fb)
        else:
            return None
