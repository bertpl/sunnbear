"""`SteffenBrent` implements the modified Brent method of Steffen et al., which can move a bound onto the midpoint.

The rest of this docstring is the record of `SteffenBrent` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - Ia - article code: none;
      - Ib - article pseudocode: Steffen et al. (2025), its Algorithm 2;
      - Ic - article text: Steffen et al. (2025), its section 2.2 and equations 3 to 5. The text keeps the tests of
        Brent's method on the step size, which Algorithm 2 leaves out, and accepts an interpolation step only between
        ``b`` and ``(a + b) / 2``, where Algorithm 2 accepts it between ``b`` and ``(3 * a + b) / 4``.
    - II - authors' code:
      - none: the article states that the authors implemented the methods in Python 3, and publishes no code.
    - III - third party:
      - rateslib's ``_brent``, which implements Algorithm 2, with Algorithm 2's midpoint ``(a + b) / 2``, and chooses
        the step by testing the function values.
    - IV - own judgment:
      - the midpoint ``(a + s) / 2`` of ``a`` and the new x-value ``s``, which only the article's figures support, and
        the other choices marked IV below.

Source per aspect:
    Every aspect follows Algorithm 2 of Steffen et al. (2025), except:
    - When the root lies between ``a`` and ``s``, the code evaluates the midpoint ``(a + s) / 2`` (IV), where
      Algorithm 2, the text and rateslib evaluate ``(a + b) / 2``, because the validation with ``(a + b) / 2`` is not
      convincing (P5): only ``(a + s) / 2`` reproduces the modified Brent method's values in the article's Figures 3,
      4, 6 and 7, and ``(a + b) / 2`` departs from them in the first iteration.
    - The code chooses the step by testing the function values, as rateslib does (III), because Algorithm 2's choice
      of step on the x-values can divide by 0 (P2): in the secant step when ``b`` equals ``b_previous``, the previous
      value of ``b``, and in the interpolation when 2 distinct x-values share a function value. Wherever Algorithm 2's
      step is defined, both choices give the same step.
    - Where ``f(a)``, ``f(b)`` and ``f(b_previous)`` are not distinct, the code bisects only when ``f(b)`` equals
      ``f(b_previous)`` (IV):
      - rateslib also bisects when they differ by less than 1e-16, an absolute threshold that makes the step depend on
        the scale of f;
      - with f multiplied by each of 4 factors from 1e-16 to 1e-300, the test suite's problems need 21 % to 48 % more
        evaluations with rateslib's threshold.
    - The code also rejects an interpolation step that is NaN (IV), which Algorithm 2's acceptance test keeps, because
      an evaluation at NaN ends the solve as ``DIVERGED``. No step is NaN on the test suite's problems, with f
      multiplied by each of 8 factors from 1e-300 to 1e300.
    - PRINCIPLE-CONFLICT (P6): the secant step computes ``fb * (b_previous - b) / (fb_previous - fb)``, which
      multiplies before it divides, where equation 4 multiplies ``f(b)`` by the quotient
      ``(b_previous - b) / (f(b_previous) - f(b))``. Computing the quotient first would resolve the conflict; on 141
      solves of the test suite's problems, computing the quotient first changes the evaluated x-values in 21 of them,
      and the evaluation count in none.
    - PRINCIPLE-GAP (P2): when ``f(s) = 0``, the code returns ``s`` at once, where Algorithm 2 first evaluates the
      midpoint, whose value can change neither the interval nor the returned x-value:
      - P2 does not say whether saving such an evaluation is a good reason to deviate, and P6 allows skipping
        comparisons, not evaluations;
      - on 141 solves of the test suite's problems, 37 end at such a zero, each with 1 evaluation fewer than
        Algorithm 2 makes; the article's case study 1 is one of them.
    - PRINCIPLE-GAP (P7): ``xtol`` is Algorithm 2's ``tol1``, but Algorithm 2 also stops once ``|f(b)| <= tol2``, and
      P7 does not say how ``xtol``, a tolerance on x, translates into a tolerance on f. The code passes 0 as ``tol2``,
      so that only an exact zero ends a solve before the interval is at most ``xtol`` wide:
      - with any ``tol2`` from 1.6e-15 to 3.2e-10, case study 1 takes the 6 iterations in the article's figures,
        where the code takes 7;
      - with ``tol2 = xtol``, 24 of 141 solves of the test suite's problems return an x-value that is not within
        ``xtol`` of a root.

Validation:
    - A - authors' results:
      - used: the 2 case studies, which `SteffenBrent` reproduces convincingly (P5):
        - the roots of both, and the modified Brent method's values in Figures 3, 4, 6 and 7, to the precision of
          reading the plots;
        - the 6 iterations in the figures, exactly in case study 2, and to within 1 in case study 1, which P5
          accepts as an experimental difference: `SteffenBrent` does not stop on ``|f(b)|`` (see the
          PRINCIPLE-GAP (P7) entry);
      - not used: Table 1, which gives mean execution times.
    - B - third-party results:
      - none found: no article by a third party that sunnbear cites publishes results of the method.
    - C - reference implementation:
      - not used: rateslib's ``_brent`` evaluates the midpoint ``(a + b) / 2``, so its x-values depart from those of
        `SteffenBrent` at the first midpoint, and its license allows only non-commercial use.

Variants:
    - `SteffenBrentConfig`, the only config, is secondary (P8); its deviation from the principles is the entry marked
      PRINCIPLE-CONFLICT (P6) above.
"""

from sunnbear._core.solvers.core import Solver, SolveState


class SteffenBrent(Solver):
    """`SteffenBrent` implements the modified Brent method of Steffen et al. (2025), as the paper's Algorithm 2.

    `SteffenBrent` keeps 2 interval bounds, ``a`` and ``b``; ``b`` is the bound with the smaller ``|f|``, and is the
    best estimate of the root. Each iteration evaluates a new x-value ``s``, from 1 of 3 steps:

    - inverse quadratic interpolation through ``a``, ``b`` and ``b_previous``, the previous value of ``b``, when the 3
      function values are distinct;
    - linear interpolation, a secant step, through ``b`` and ``b_previous``, when the 3 function values are not
      distinct but ``f(b)`` and ``f(b_previous)`` differ;
    - bisection, in all other cases, and in place of an interpolation step that does not land strictly between ``b``
      and ``(3 * a + b) / 4``.

    In the first iteration, ``b_previous`` is ``a``, so the first step is a secant step.

    ``s`` becomes the new ``b``, and the new ``a`` is chosen so that the interval keeps the root:

    - when ``f(a)`` and ``f(s)`` have the same sign, the old ``b`` becomes the new ``a``, as in Brent's method;
    - otherwise the root lies between ``a`` and ``s``, and `SteffenBrent` evaluates their midpoint ``m = (a + s) / 2``;
      when ``f(m)`` and ``f(s)`` differ in sign, ``m`` becomes the new ``a``.

    The second case is the paper's modification of Brent's method. Finally, ``a`` and ``b`` swap where needed, so that
    ``b`` keeps the smaller ``|f|``.

    Unlike Brent's method, Algorithm 2 has no tests on the step size that force a bisection once the interpolation
    steps stop shrinking, so on some functions the interval shrinks slowly.

    The solve ends once ``|b - a| <= xtol``, and returns ``b``, which then lies within ``xtol`` of a root; it ends
    earlier, and returns ``s``, once ``f(s) = 0``.

    The paper's title says that the modification halves the interval in every iteration, but Algorithm 2 does not
    guarantee that the interval halves:

    - when the root lies between ``a`` and ``m``, ``f(m)`` has the sign of ``f(s)``, so ``m`` does not replace ``a``,
      and the new interval runs from ``a`` to ``s``, more than half the old interval when ``s`` lies on ``b``'s side
      of ``(a + b) / 2``;
    - when ``f(a)`` and ``f(s)`` have the same sign, the new interval from ``b`` to ``s`` can keep up to 3/4 of the
      old interval.

    An iteration can evaluate the function twice, and the stopping criterion is the paper's own, so `SteffenBrent`
    writes its own loop, not `BracketingSolver`'s.

    References:
        - Steffen, V., Della Pasqua, C. C., de Oliveira, M. S. and da Silva, E. A. (2025). Halving interval
          guaranteed for Dekker and Brent root finding methods. Examples and Counterexamples 7, 100173. Its
          Algorithm 2 is the method, and the test suite reproduces its 2 case studies and the modified Brent
          method's values in its Figures 3, 4, 6 and 7. https://doi.org/10.1016/j.exco.2024.100173
        - Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. The
          Computer Journal 14(4), 422-425. Steffen et al. modify Brent's method. https://doi.org/10.1093/comjnl/14.4.422
        - rateslib's ``_brent``, in ``rateslib.dual.ift``, which the function ``ift_1dim`` runs when it is given the
          method ``modified_brent``; https://github.com/attack68/rateslib. ``_brent`` implements Algorithm 2.
    """

    name = "steffen_brent"
    version = 2

    def _solve(self, state: SolveState) -> float:
        """Run Algorithm 2 of the paper and return ``b``.

        Each iteration:

        - chooses ``s`` and evaluates it;
        - ends the solve if ``f(s) = 0``;
        - chooses the new ``a``, evaluating the midpoint of ``a`` and ``s`` where the paper's modification needs it;
        - swaps ``a`` and ``b`` where ``|f(a)| < |f(b)|``.

        The loop ends once ``|b - a| <= xtol``.
        """
        interval = state.interval
        a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb
        if abs(fa) < abs(fb):
            a, b, fa, fb = b, a, fb, fa
        b_previous, fb_previous = a, fa
        while abs(b - a) > state.xtol:
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
                # The step is a linear interpolation through b and b_previous, the paper's equation 4.
                s = b - fb * (b_previous - b) / (fb_previous - fb)
            else:
                s = (a + b) / 2.0
            # An interpolation step that overflows to inf or nan fails this comparison too, so it becomes a bisection.
            accepted_range_end = (3.0 * a + b) / 4.0
            if not min(b, accepted_range_end) < s < max(b, accepted_range_end):
                s = (a + b) / 2.0

            # --- the evaluation at s ------------
            fs = state.f(s)
            state.x_best = s
            if fs == 0.0:
                return s

            # --- the new interval ---------------
            b_previous, fb_previous = b, fb
            # Signs are compared directly, where the paper multiplies them: the product of 2 small function values can
            # underflow to 0.
            if (fa > 0.0) == (fs > 0.0):
                a, fa = b, fb
            else:
                m = (a + s) / 2.0
                fm = state.f(m)
                if (fm > 0.0 > fs) or (fm < 0.0 < fs):
                    # The root lies between m and s, so m replaces a: the paper's modification.
                    a, fa = m, fm
            b, fb = s, fs
            if abs(fa) < abs(fb):
                a, b, fa, fb = b, a, fb, fa
        return b
