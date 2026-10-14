"""`CARF` implements Gao's Curvature-Adaptive Root Finder, which clips quadratic or power interpolation steps.

The rest of this docstring is the record of `CARF` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - Ia - article code: none;
      - Ib - article pseudocode: none;
      - Ic - article text: Gao (2026), its section 2, which states the method in prose and equations, and its
        Appendix A, which derives the power step in 3 more forms.
    - II - authors' code:
      - none public: the article's section 3 mentions the author's Python program, and its data availability
        statement offers data on request.
    - III - third party:
      - Brent (1971), section 3: the test that compares a step with half the step before last, from Brent's method,
        whose criteria the article says it borrows.
    - IV - own judgment:
      - the readings of the article's open details that match the most of its Table 4, and the formulas that the
        article does not give; the exceptions below name each.

Source per aspect:
    Every aspect follows section 2 of Gao (2026), except those below. An exception that compares readings gives the
    number of the 45 evaluation counts of the article's Table 4 that each reading matches exactly; `CARF` matches 33.
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound, as for every
      solver; the article requires ``f(a) * f(b) < 0``, so it does not state this case.
    - JUDGMENT-CALL: the article's limit on the number of iterations, 200 in its Table 4, is left out, so the
      evaluation budget ends a long solve, as for every solver. The article counts a solve that reaches its limit as
      a failure.
    - JUDGMENT-CALL: the article gives no formula for the chord's zero, the first x-value before its clip. The code
      computes ``(a * f(b) - b * f(a)) / (f(b) - f(a))``, the form that `Pegasus` and `ModAB` take from their
      sources; ``a - f(a) * (b - a) / (f(b) - f(a))`` matches 35, including all 33 that `CARF` matches.
    - The quadratic's zero follows IV, since the article gives no formula: the code writes the quadratic around the
      interior x-value ``t`` in forms that avoid cancellation, takes the zero nearer ``t`` when it lies in ``[a, b]``
      and the other zero otherwise, and the zero of the line when the quadratic's leading coefficient is 0. Of 4 other
      formulas tried, none matches more than 33.
    - A negative discriminant of the quadratic, which only rounding produces, is clamped to 0 (IV); no solve of
      Tables 3 and 4 needs the clamp. When the discriminant and the quadratic's slope at ``t`` are both 0, which
      underflow can produce, the next division is by 0: at the benchmark's smallest allowed values of ``xtol``, the
      solves of x^19 on 4 of its 5 intervals in Table 4 then end as ``SOLVER_ERROR``.
    - When the 2 logarithms of the power step round to the same value, which the article does not cover, ``t*`` is
      the midpoint of the active interval, clipped with ``θ = 0.5`` (IV); of Tables 3 and 4, only Table 4's function
      3 over [-1e6, 1e6], written 3[-1e6, 1e6] below, meets this case.
    - PRINCIPLE-GAP (P6): the article writes the power step in 4 forms, equal in exact arithmetic, and P6 does not say
      which written form counts. The code keeps the form in which section 2 states the method; Appendix A's form
      ``a + (b - a) * r * r^sigma``, with ``sigma`` as Appendix A defines it, matches 35, including all 33 that `CARF`
      matches, and keeps Table 3's totals within 1.5 %.
    - The acceptance test follows Brent (1971): a step is accepted when it is shorter than half the step before last.
      The article's own test, against half the width of the interval 2 iterations back, is undefined in the first
      iteration, and the validation with that test is not convincing (P2): the article's test matches 15, and with
      ``eps1 = 0`` it almost never clips on (x - 3)^3 over [0, 5] and on Table 2's x^5 and x^7, which then do not
      converge within 5,000 evaluations.
    - The last step and the step before last, which the acceptance test needs, follow IV: they start at the initial
      interval's width, as in Brent's procedure ``zero``, and every step, accepted or clipped, shifts them. Brent's
      rule after a bisection, applied to a clip, sets both to half the active interval's width and matches 21; a start
      at infinity matches 29.
    - The interval after a sign change follows IV: the article takes the shorter of "two sign-changing sub-intervals
      containing" the new x-value, without saying which 2. The code takes the shorter of the active interval, with
      the new x-value inside, and the interval from the new x-value to the bound outside the active interval, with the
      old ``t`` inside; on a tie, the active one. Always the active interval matches 19, always the other 24.
    - The stop test checks only the interior x-value (IV), where the article tests each new x-value: a new x-value
      that becomes an interval bound does not end the solve, however small its ``|f|``. Testing it too matches 31.
    - The returned x-value, which the article does not state, is the interior x-value ``t`` (IV); when the solve
      ends because the active interval is narrower than ``xtol``, ``t`` is a bound of the active interval, so it lies
      within ``xtol`` of a root.
    - Translation of ``xtol`` (P7): ``xtol`` is the article's ``eps2``, and its ``eps1`` is 0:
      - the width test is ``b* - a* < xtol``, and the test ``|f(t)| < eps1``, which then never holds, becomes
        ``f(t) = 0``; a new x-value with ``f = 0`` is not taken as a sign change, so it becomes the interior x-value,
        which that test checks;
      - the article's Tables 3 and 4 use ``eps1 = 1e-15``; with ``eps1 = 0``, Table 3's totals lie 3.7 to 8.6 % above
        the article's.

Validation:
    - A - authors' results:
      - used: Table 4, 33 of its 45 evaluation counts exactly, and Table 3, its 3 totals within 1.5 %, both with
        ``eps1 = 1e-15``. With that ``eps1``, each solve of Table 4's functions 3 to 6, which have multiple roots,
        ends once ``|f(t)| < 1e-15``, at an x-value between 4e-6 and 0.13 from the root.
      - PRINCIPLE-CONFLICT (P5): the reproduction is not convincing as a whole, for 2 reasons:
        - Table 2 is not reproduced, and no explanation is known:
          - at ``xtol = 1e-10``, the tolerance at which SciPy's ``brentq`` reproduces the table's column "Brentq",
            `CARF` takes 53 and 61 evaluations on Table 2's x^5 and x^7, against 37 and 35;
          - no other value of ``eps1`` or formula of a step that was tried closes the gap, and no reading of the
            article's open details that was tried reproduces Table 2 together with Table 4: the closest to Table 2,
            at 39 and 36, matches 8 of Table 4's counts;
          - of the article's tables, only Table 2 shows solves that reach a tight tolerance at a multiple root, as
            those of `CARF` do with ``eps1 = 0``.
        - On the widest intervals of functions 1 to 4, 10 of Table 4's counts differ by 3 to 59. Each of the 10
          changes with the formula of the chord's zero, the quadratic's zero or the power step, whose forms in the
          author's program the article does not state, but only 3 reach the article's count with another formula.
        The author's program (II) would resolve the conflict.
      - PRINCIPLE-GAP (P2): P2 lets a solver whose validation is not convincing use the next-ranked source, here the
        author's program, which is not public; P2 does not say whether sunnbear must request it, and the code follows
        the article without it.
      - PRINCIPLE-CONFLICT (P5): the tests check Table 4's other 12 counts for convergence only, and their test data
        state causes that do not all hold, where P5 accepts a difference of 1 marked ``UNSTATED_RUN_DETAILS`` and asks
        that an unverified cause never be stated as fact:
        - 8[2e-4, 2] and 9[2e-4, 1] differ by 1; on 9[2e-4, 1], the stated cause, a 1-ulp difference in the last
          step, gives 9, not the article's 7;
        - the stated cause of the other 10, that ``h = (f(t) - f(a)) / (f(b) - f(a))`` lies within rounding error of
          a limit that picks the kind of step, does not hold on 1[-1e4, 1e4] and 1[-1e10, 1e10].
        Accepting the 2 counts that differ by 1, marked ``UNSTATED_RUN_DETAILS``, and stating for the 10 only that
        their counts change with the formulas of the steps, would resolve the conflict.
      - TBD: Table 1, its functions f and g: at ``xtol = 1e-8``, the tolerance at which SciPy's ``brentq``
        reproduces the table's column "Brentq", `CARF` takes 28 and 38 evaluations against 29 and 32;
      - not used: Table 1's third function, whose random poles and weights the article does not publish.
    - B - third-party results:
      - none found: no third party is known to publish results of the method.
    - C - reference implementation:
      - none found: the author's program is not public, and no third-party implementation is known.

Variants:
    - `CARFConfig`, the only config, is secondary (P8); its behavior deviates from no principle, and the record's
      entries marked PRINCIPLE-CONFLICT concern its validation.
"""

import math

from sunnbear._core.solvers.core import Solver, SolveState

# The paper's constants, which clip an x-value into the middle part of an interval: a fraction θ of the interval's
# width at each end is out of bounds. θ0 places the first x-value; θ1, θ2 and θ3 clip the later x-values, and the kind
# of step that produced an x-value decides which of the 3 applies.
_THETA_0 = 0.1
# θ1 clips a quadratic step when the quadratic through the 3 points is monotone.
_THETA_1 = 0.15
# θ2 clips a power step.
_THETA_2 = 0.15
# θ3 clips a quadratic step when the 3 function values are not monotone; a clip with θ3 always yields the midpoint.
_THETA_3 = 0.5


class CARF(Solver):
    """`CARF` implements the Curvature-Adaptive Root Finder of Gao (2026), reconstructed from the paper and its results.

    `CARF` keeps an interval ``[a, b]`` and an interior x-value ``t``, strictly inside it, and knows the function
    value at all 3. The first ``t`` is the zero of the chord through the bounds,
    ``(a * f(b) - b * f(a)) / (f(b) - f(a))``, clipped into the middle 80 % of the interval (``θ0 = 0.1``). Each
    iteration:

    - **selects the active interval:** ``[a, t]`` or ``[t, b]``, the part that holds the sign change, which the paper
      calls the "active bracket", with bounds ``a*`` and ``b*`` and width ``w* = b* - a*``;
    - **interpolates a candidate ``t*``,** with ``r = (t - a) / (b - a)`` and ``h = (f(t) - f(a)) / (f(b) - f(a))``:

      - when ``r^2 <= h <= 1 - (1 - r)^2``, the quadratic through ``(a, f(a))``, ``(t, f(t))`` and ``(b, f(b))`` is
        monotone on ``[a, b]``, and ``t*`` is its zero in ``[a, b]``, as `_quadratic_zero` computes it;
      - when ``h`` lies in ``(0, 1)`` outside that band, the 3 function values are monotone but the quadratic is not,
        and ``t*`` is the zero of the power function ``alpha * (x - a)^beta + gamma`` through the 3 points, in the
        form of the paper's section 2: ``t* = a + (b - a) * r^xi``, with
        ``xi = log(1 - f(b) / f(a)) / (log(1 - f(b) / f(a)) - log(1 - f(t) / f(a)))``. When the 2 logarithms round to
        the same value, the denominator of ``xi`` is 0, and ``t*`` is the midpoint of the active interval, clipped as
        when the 3 function values are not monotone;
      - when ``h`` lies outside ``(0, 1)``, the 3 function values are not monotone, and ``t*`` is the quadratic's zero;

    - **accepts or clips ``t*``:** a step is the distance from one x-value to the next. ``t*`` becomes the new x-value
      ``t_new`` when it lies inside the active interval and the step from ``t`` is shorter than half the step before
      last, the test of Brent's method, from which the paper says it borrows its criteria. Otherwise ``t_new`` is ``t*``
      clipped into ``[a* + θ * w*, b* - θ * w*]``, where ``θ`` is 0.15, or 0.5 when the 3 function values are not
      monotone, which clips ``t*`` to the midpoint. Accepted and clipped steps both update the last step and the step
      before last, and before the first iteration both are set to the width of the initial interval;
    - **updates the interval:** when ``f(t_new)`` and ``f(t)`` differ in sign, the new interval is the shorter of these
      2 intervals, or the first on a tie:

      - the active interval, with ``t_new`` as its interior x-value;
      - the interval from ``t_new`` to the bound of ``[a, b]`` outside the active interval, with the old ``t`` as its
        interior x-value.

      Otherwise, the new interval is the active interval, with ``t_new`` as its interior x-value. A ``t_new`` with
      ``f(t_new) = 0`` is not a sign change, so it becomes the interior x-value, and the solve ends at it.

    The solve ends once ``f(t) = 0``, or once the active interval is narrower than ``xtol``, and returns ``t``, which
    then lies within ``xtol`` of a root. The stop test checks only the interior x-value: a ``t_new`` that becomes a
    bound of the interval does not end the solve, however small its ``|f|``.

    The paper stops once ``|f(t)| < eps1`` or the active interval is narrower than ``eps2 + |t| * eps1``; `CARF` uses
    ``xtol`` as ``eps2`` and 0 as ``eps1``, and replaces the test ``|f(t)| < 0``, which never holds, with ``f(t) = 0``.

    A known caveat: the old ``t`` can stay the interior x-value while it lies far from the root.

    - **Cause:** a sign change near the root makes the interval from ``t_new`` to the bound outside the active
      interval the shorter one, and that interval keeps the old ``t`` inside.
    - **Effect:** the next steps are then clipped, and each shrinks the interval by only 15 %, or halves it when the 3
      function values are not monotone, so the solve can take many more evaluations than usual, up to its budget.
    - **Occurrence:** it occurs on some of the paper's test problems, including problems whose published counts
      `CARF` reproduces, such as the 8th function of the paper's Table 4 over ``[2e-4, 81]``; on others, it occurs when
      1 candidate ``t*`` is rounded differently by 1 ulp.

    The paper's proof guarantees only that each step shrinks the interval to at most 70 % of its width. A power step
    evaluates 2 logarithms and a power, so `CARF`'s flop counts can exceed those of the other solvers.

    `CARF` keeps an interior x-value besides the 2 bounds, and stops by its own criterion, so it writes its own loop,
    not `BracketingSolver`'s.

    References:
        - Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics Letters
          178, 109928. Its section 2 describes the method and its constants, and its Appendix A derives the power step
          in 3 more forms; the test suite compares `CARF` with the results of its Tables 3 and 4.
          https://doi.org/10.1016/j.aml.2026.109928
        - Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. The Computer
          Journal 14(4), 422-425. It describes the test that compares a step with half the step before last, which
          `CARF` borrows.
          https://doi.org/10.1093/comjnl/14.4.422
        - Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear
          function without using derivatives. Advances in Engineering Software 28(3), 145-149. Gao's Table 4 runs on
          the 45 test problems of this paper's Table 2. Gao's reference list cites it under the title "A new method
          for finding the zero of a function", in Computers & Structures 64 (1997) 265-271, which holds no such paper.
          https://doi.org/10.1016/S0965-9978(96)00051-8
    """

    name = "carf"
    version = 1

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with the paper's description
        """Run CARF's iterations and return the interior x-value ``t``.

        Each iteration, as the class docstring describes:

        - selects the active interval, and ends the solve if the stop test holds;
        - interpolates ``t_star``, and accepts or clips it;
        - evaluates the new x-value, and updates the interval.

        The variables follow the paper's names, spelled as Python identifiers: ``a_active`` and ``b_active`` are its
        ``a*`` and ``b*``, and ``t_star`` is its ``t*``.
        """
        interval = state.interval
        a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb

        # --- the first x-value ------------------
        width = b - a
        t = (a * fb - b * fa) / (fb - fa)
        t = max(min(t, b - _THETA_0 * width), a + _THETA_0 * width)
        ft = state.f(t)
        state.x_best = t
        step_before_last = last_step = width
        while True:
            # --- the active interval ------------
            # Signs are compared directly, not by multiplying the function values as the paper does, because the
            # product of 2 small function values can underflow to 0.
            is_sign_change_below_t = (fa < 0.0 < ft) or (ft < 0.0 < fa)
            if is_sign_change_below_t:
                a_active, b_active = a, t
            else:
                a_active, b_active = t, b
            if self._is_converged(t, ft, b_active - a_active, state.xtol):
                return t

            # --- the candidate t_star -----------
            r = (t - a) / (b - a)
            h = (ft - fa) / (fb - fa)
            if r * r <= h <= 1.0 - (1.0 - r) ** 2:
                t_star, theta = self._quadratic_zero(a, t, b, fa, ft, fb), _THETA_1
            elif 0.0 < h < 1.0:
                log_one_minus_fb_over_fa = math.log(1.0 - fb / fa)
                log_one_minus_ft_over_fa = math.log(1.0 - ft / fa)
                if log_one_minus_fb_over_fa == log_one_minus_ft_over_fa:
                    # The denominator of xi is 0: take the midpoint, which a clip with θ3 also yields.
                    t_star, theta = 0.5 * (a_active + b_active), _THETA_3
                else:
                    xi = log_one_minus_fb_over_fa / (log_one_minus_fb_over_fa - log_one_minus_ft_over_fa)
                    t_star, theta = a + (b - a) * r**xi, _THETA_2
            else:
                t_star, theta = self._quadratic_zero(a, t, b, fa, ft, fb), _THETA_3

            # --- the new x-value t_new ----------
            if a_active < t_star < b_active and abs(t_star - t) < 0.5 * abs(step_before_last):
                t_new = t_star
            else:
                active_width = b_active - a_active
                t_new = max(min(t_star, b_active - theta * active_width), a_active + theta * active_width)
            step_before_last, last_step = last_step, t_new - t
            ft_new = state.f(t_new)
            state.x_best = t_new

            # --- the new interval ---------------
            if (ft_new < 0.0 < ft) or (ft < 0.0 < ft_new):
                # On a sign change, the new interval is the shorter of the active interval, with t_new inside, and
                # the interval from t_new to the bound outside the active interval, with t inside.
                if is_sign_change_below_t:
                    if b - t_new < t - a:
                        a, fa = t_new, ft_new
                    else:
                        b, fb, t, ft = t, ft, t_new, ft_new
                elif t_new - a < b - t:
                    b, fb = t_new, ft_new
                else:
                    a, fa, t, ft = t, ft, t_new, ft_new
            elif is_sign_change_below_t:
                b, fb, t, ft = t, ft, t_new, ft_new
            else:
                a, fa, t, ft = t, ft, t_new, ft_new

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _quadratic_zero(a: float, t: float, b: float, fa: float, ft: float, fb: float) -> float:
        """Return the zero in ``[a, b]`` of the quadratic through ``(a, fa)``, ``(t, ft)`` and ``(b, fb)``.

        The quadratic is written around ``t``, as ``q(t + u) = c2 * u^2 + c1 * u + ft``. Of the quadratic's 2 zeros,
        the one nearer ``t`` is at ``u = ft / c2_times_u_far`` and the other at ``u = c2_times_u_far / c2``, with
        ``c2_times_u_far = -(c1 + sign(c1) * sqrt(c1^2 - 4 * c2 * ft)) / 2``, which is ``c2`` times the ``u`` of the
        zero farther from ``t``; these forms avoid the cancellation of the textbook formula.

        When rounding puts neither zero in ``[a, b]``, the zero farther from ``t`` is returned, and the caller's clip
        moves it into the active interval.
        """
        slope_a_t = (ft - fa) / (t - a)
        slope_t_b = (fb - ft) / (b - t)
        c2 = (slope_t_b - slope_a_t) / (b - a)
        c1 = slope_a_t + c2 * (t - a)
        if c2 == 0.0:
            return t - ft / c1
        else:
            discriminant = max(c1 * c1 - 4.0 * c2 * ft, 0.0)
            c2_times_u_far = -0.5 * (c1 + math.copysign(math.sqrt(discriminant), c1))
            zero_near_t = t + ft / c2_times_u_far
            if a <= zero_near_t <= b:
                return zero_near_t
            else:
                return t + c2_times_u_far / c2

    @staticmethod
    def _is_converged(t: float, ft: float, active_width: float, xtol: float) -> bool:
        """Return whether the stop test holds at the interior x-value ``t``.

        The test holds once ``f(t) = 0`` or the active interval is narrower than ``xtol``, and does not use ``t``.
        The test suite overrides this method to apply the paper's stop test and tolerances, the relative tolerance
        ``|t| * eps1`` included, when it reproduces the paper's tables.
        """
        return ft == 0.0 or active_width < xtol
