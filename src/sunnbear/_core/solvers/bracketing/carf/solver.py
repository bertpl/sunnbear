"""`CARF` implements Gao's Curvature-Adaptive Root Finder, which clips quadratic or power interpolation steps."""

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

    The method keeps a bracket ``[a, b]`` and an interior x-value ``t``, strictly inside it, and knows the function
    value at all 3. The first ``t`` is the zero of the chord through the bounds, clipped into the middle 80 % of the
    interval (``θ0 = 0.1``). Each iteration:

    - **selects the active bracket:** ``[a, t]`` or ``[t, b]``, the part that holds the sign change, with bounds ``a*``
      and ``b*`` and width ``w* = b* - a*``;
    - **interpolates a candidate ``t*``,** with ``r = (t - a) / (b - a)`` and ``h = (f(t) - f(a)) / (f(b) - f(a))``:

      - when ``r^2 <= h <= 1 - (1 - r)^2``, the quadratic through the 3 points is monotone on ``[a, b]``, and ``t*`` is
        its root;
      - when ``h`` lies in ``(0, 1)`` outside that band, the 3 function values are monotone but the quadratic is not,
        and ``t*`` is the root of the power function ``alpha * (x - a)^beta + gamma`` through the 3 points:
        ``t* = a + (b - a) * r^xi``, with ``xi = log(1 - f(b) / f(a)) / (log(1 - f(b) / f(a)) - log(1 - f(t) / f(a)))``;
      - when ``h`` lies outside ``(0, 1)``, the 3 function values are not monotone, and ``t*`` is the quadratic's root;

    - **accepts or clips ``t*``:** a step is the distance from one x-value to the next. ``t*`` becomes the new x-value
      ``t_new`` when it lies inside the active bracket and the step from ``t`` is shorter than half the step before
      last; otherwise ``t_new`` is ``t*`` clipped into ``[a* + θ * w*, b* - θ * w*]``, where ``θ`` is 0.15, or 0.5 when
      the 3 function values are not monotone, which clips ``t*`` to the midpoint;
    - **updates the bracket,** as the bullet *The bracket after a sign change* below describes.

    The solve ends once ``f(t) = 0``, or once the active bracket is narrower than ``xtol``, and returns ``t``, which
    then lies within ``xtol`` of a root.

    The paper stops once ``|f(t)| < eps1`` or the active bracket is narrower than ``eps2 + |t| * eps1``; `CARF` uses
    ``xtol`` as ``eps2`` and 0 as ``eps1``, and replaces the test ``|f(t)| < 0``, which never holds, with ``f(t) = 0``.

    The paper's code is not public, and the paper leaves parts of the method open or describes them ambiguously.
    `CARF` makes these choices, each chosen to reproduce the paper's Tables 3 and 4 as closely as possible:

    - **The acceptance test:** the paper compares the step ``|t* - t|`` with half "the width of the bracket two steps
      ago". `CARF` compares the step with half the step before last, the criterion of Brent's method, which the paper
      says it borrows.

      Read the paper's way, the test never clips while the x-values approach the root from one side: on
      ``(x - 3)^3`` over ``[0, 5]``, the solve then runs to the paper's limit of 200 iterations, while the paper reports
      28 evaluations. Accepted and clipped steps both update the last step and the step before last, and before the
      first iteration both are set to the width of the initial interval.
    - **The bracket after a sign change:** when ``f(t_new)`` and ``f(t)`` differ in sign, the paper takes the shorter
      of "two sign-changing sub-intervals containing" ``t_new``. `CARF` takes the shorter of these 2 brackets:

      - the active bracket, with ``t_new`` as its interior x-value;
      - the bracket from ``t_new`` to the bound of ``[a, b]`` outside the active bracket, with the old ``t`` as its
        interior x-value.

      When the signs agree, the new bracket is the active bracket, with ``t_new`` as its interior x-value.
    - **A function value of 0 is not a sign change:** a sign change means ``f(t_new) * f(t) < 0``, so a ``t_new``
      with ``f(t_new) = 0`` becomes the interior x-value, and the solve ends at it.
    - **The stop test checks only the interior x-value:** a ``t_new`` that becomes a bound of the bracket does not end
      the solve, however small its ``|f|``. With the paper's ``eps1 > 0``, the evaluation counts of Table 4 depend on
      this choice.
    - **The quadratic's root:** the paper does not say how it computes the root. `CARF` writes the quadratic around
      ``t`` and takes its root in ``[a, b]`` from the formula that avoids cancellation.

      On intervals as wide as ``[-1e4, 1e4]``, ``h`` often lies within rounding error of 0 or 1, the limits that
      choose the kind of step, so the evaluation counts depend on this formula, and on some of those intervals `CARF`
      does not reproduce Table 4.
    - **A power step that cannot be computed:** when the 2 logarithms in the formula for ``xi`` round to the same
      value, the denominator of ``xi`` is 0. `CARF` then takes the midpoint of the active bracket; the paper does not
      cover this case.

    Signs of function values are compared directly, where the paper multiplies them: the product of 2 small function
    values can underflow to 0. The paper's limit of 200 iterations is left out: the solve's evaluation budget ends a
    solve instead.

    A known caveat: the old ``t`` can stay the interior x-value while it lies far from the root.

    - **Cause:** a sign change near the root makes the bracket from ``t_new`` to the bound outside the active bracket
      the shorter one, and that bracket keeps the old ``t`` inside.
    - **Effect:** the next steps are then clipped, and each shrinks the bracket by only 15 %, so the solve can take
      many more evaluations than usual, up to its budget.
    - **Occurrence:** none of the paper's test problems triggers this slowdown, but one of them does when the
      quadratic's root at one of its steps moves by 1 ulp.

    The paper's proof guarantees only that each step shrinks the bracket to at most 70 % of its width. A power step
    evaluates 2 logarithms and a power, so `CARF`'s flop counts can exceed those of the other solvers.

    `CARF` keeps an interior x-value besides the 2 bounds, and stops by its own criterion, so it writes its own loop,
    not `BracketingSolver`'s.

    References:
        - Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics Letters
          178, 109928. The method and its constants, and Tables 3 and 4, which the test suite compares `CARF` with.
          https://doi.org/10.1016/j.aml.2026.109928
        - Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. The Computer
          Journal 14(4), 422-425. The test that compares a step with half the step before last, which `CARF` borrows.
          https://doi.org/10.1093/comjnl/14.4.422
    """

    name = "carf"
    version = 1

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with the paper's description
        """Run CARF's iterations and return the interior x-value ``t``.

        Each iteration, as the class docstring describes:

        - selects the active bracket, and ends the solve if the stop test holds;
        - interpolates ``t_star``, and accepts or clips it;
        - evaluates the new x-value, and updates the bracket.

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
            # --- the active bracket -------------
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
                t_star, theta = self._quadratic_root(a, t, b, fa, ft, fb), _THETA_1
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
                t_star, theta = self._quadratic_root(a, t, b, fa, ft, fb), _THETA_3

            # --- the new x-value t_new ----------
            if a_active < t_star < b_active and abs(t_star - t) < 0.5 * abs(step_before_last):
                t_new = t_star
            else:
                active_width = b_active - a_active
                t_new = max(min(t_star, b_active - theta * active_width), a_active + theta * active_width)
            step_before_last, last_step = last_step, t_new - t
            ft_new = state.f(t_new)
            state.x_best = t_new

            # --- the new bracket ----------------
            if (ft_new < 0.0 < ft) or (ft < 0.0 < ft_new):
                # On a sign change, the new bracket is the shorter of the active bracket, with t_new inside, and the
                # bracket from t_new to the bound outside the active bracket, with t inside.
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
    def _quadratic_root(a: float, t: float, b: float, fa: float, ft: float, fb: float) -> float:
        """Return the root in ``[a, b]`` of the quadratic through ``(a, fa)``, ``(t, ft)`` and ``(b, fb)``.

        The quadratic is written around ``t``, as ``q(t + u) = c2 * u^2 + c1 * u + ft``. Of the quadratic's 2 roots,
        the one nearer ``t`` is at ``u = ft / root_term`` and the other at ``u = root_term / c2``, with
        ``root_term = -(c1 + sign(c1) * sqrt(c1^2 - 4 * c2 * ft)) / 2``; these forms avoid the cancellation of the
        textbook formula.

        When rounding puts neither root in ``[a, b]``, the root farther from ``t`` is returned, and the caller's clip
        moves it into the bracket.
        """
        slope_a_t = (ft - fa) / (t - a)
        slope_t_b = (fb - ft) / (b - t)
        c2 = (slope_t_b - slope_a_t) / (b - a)
        c1 = slope_a_t + c2 * (t - a)
        if c2 == 0.0:
            return t - ft / c1
        else:
            discriminant = max(c1 * c1 - 4.0 * c2 * ft, 0.0)
            root_term = -0.5 * (c1 + math.copysign(math.sqrt(discriminant), c1))
            root_near_t = t + ft / root_term
            if a <= root_near_t <= b:
                return root_near_t
            else:
                return t + root_term / c2

    @staticmethod
    def _is_converged(t: float, ft: float, active_width: float, xtol: float) -> bool:
        """Return whether the stop test holds at the interior x-value ``t``.

        The test holds once ``f(t) = 0`` or the active bracket is narrower than ``xtol``, and does not use ``t``; a
        subclass that overrides this method can use ``t`` for the paper's relative tolerance ``|t| * eps1``.
        """
        return ft == 0.0 or active_width < xtol
