"""`ModAB` implements the modified Anderson-Björck method, which switches between bisection and Anderson-Björck."""

import math

from sunnbear._core.solvers.core import IntervalBound, Solver, SolveState
from sunnbear._core.solvers.core.stopping import interval_root_if_converged

from .variant import ModABVariant

# With this factor, the Anderson-Björck steps of the "algorithms_2026" variant may fall 4 steps behind bisection before
# the solve falls back to bisection: 16 = 2^4 (the paper's section 4.2).
_FALLBACK_THRESHOLD_FACTOR = 16.0


class ModAB(Solver):
    """`ModAB` implements the modified Anderson-Björck method, in the 2 versions that its authors published in 2026.

    The method combines bisection with the Anderson-Björck method, the modified regula falsi method of `AndersonBjorck`.
    `ModAB` keeps the interval bounds ``x1 < x2`` with their function values ``y1`` and ``y2``, and runs in 1 of 2
    modes, starting with bisection:

    - **bisection:** the new x-value ``x3`` is the midpoint. After evaluating ``y3 = f(x3)``, the method switches to
      Anderson-Björck mode when the function looks close to a straight line on the interval:
      ``|ym - y3| < k*(|y3| + |ym|)``, where ``ym = (y1 + y2) / 2`` is the value of the secant at the midpoint,
      ``k = r^2``, and ``r = 1 - |ym / (y2 - y1)|`` measures how symmetric ``y1`` and ``y2`` are;
    - **Anderson-Björck:** ``x3`` is the zero of the secant, ``(x1*y2 - y1*x2) / (y2 - y1)``.

    ``x3`` replaces the bound whose function value has the sign of ``y3``.

    In Anderson-Björck mode, when the same bound is retained in 2 iterations in a row, its stored function value is
    multiplied by the factor of `AndersonBjorck`, ``m = 1 - y3 / y_moved``, where ``y_moved`` is the function value at
    the replaced bound; where ``m`` is not positive, the factor is 0.5.

    The switch to Anderson-Björck mode sets a threshold in proportion to the interval width, and every Anderson-Björck
    step halves the threshold; once the interval is wider than the threshold, the method falls back to bisection.

    ``variant``, a value of `ModABVariant`, picks 1 of the 2 versions:

    - ``"algorithms_2026"``, the method of Ganchovski et al. (2026), ported from the C# code of the paper's Table A1.
      The switch sets the threshold to `_FALLBACK_THRESHOLD_FACTOR` times the interval width.
    - ``"safeguarded_2026"``, the safeguarded method of Tomov and Ganchovski (2026), ported from the authors' C# code
      ``SgModAB.cs``. It differs from ``"algorithms_2026"`` in these ways:

      - **No scaling in the first Anderson-Björck step:** in ``"algorithms_2026"``, the bisection step that switches
        already records the bound that it retains, so a first Anderson-Björck step that retains the same bound scales
        that bound's stored function value. ``"safeguarded_2026"`` starts each Anderson-Björck phase with no bound
        recorded.
      - **True function values kept apart:** ``"safeguarded_2026"`` scales copies of ``y1`` and ``y2``, the
        ordinates that only the secant reads, and resets the ordinates to ``y1`` and ``y2`` at each switch. In
        ``"algorithms_2026"``, as its C# code shows, a scaled value replaces the stored function value, and stays
        stored after a fallback to bisection, where the switching test reads it.
      - **Fallback rule:** the switch sets the threshold to `_SAFEGUARDED_FALLBACK_THRESHOLD_FACTOR` times the
        interval width after ``x3`` replaces a bound. An Anderson-Björck step that leaves the interval wider than the
        threshold still continues the phase, as a residual exception, if ``|y3|`` is below half the smaller of
        ``|y1|`` and ``|y2|`` before the step; at most `_SAFEGUARDED_MAX_RESIDUAL_STEPS` steps in a row may be
        residual exceptions.
      - **Forms of the steps:** the secant's zero is ``(b/den)*x1 + (a/den)*x2``, projected into the interval, where
        ``a`` and ``b`` are the magnitudes of the ordinates at ``x1`` and ``x2``, and ``den = a + b``; where ``den``
        overflows, ``a`` and ``b`` are halved first. The midpoint is ``0.5*x1 + 0.5*x2``. The switching test is
        ``|ym - y3| < k*|ym| + k*|y3|``, and is skipped where ``y2 - y1`` overflows.

    Both variants check the shared stopping criterion at the 2 points of each iteration where their C# code checks its
    own:

    - after computing ``x3`` and before evaluating it, the solve ends once the interval is at most ``2*xtol`` wide, and
      returns the interval's midpoint, which then lies within ``xtol`` of a root;
    - after evaluating ``x3``, the solve ends once ``y3 = 0``, and returns ``x3``.

    `ModAB` follows each variant's C# code where its paper differs from it or leaves a detail out, and departs from
    that code in its stopping criterion, its iteration limit, and code paths that can never run in `ModAB`:

    - **Stopping criterion:** before evaluating ``x3``, the C# code ends the solve once the interval is at most
      ``aTol + rTol*|x3|`` wide, for an absolute tolerance ``aTol`` and a relative tolerance ``rTol``, and returns
      ``x3``, not the interval's midpoint.
    - **No iteration limit:** the C# code stops after 200 iterations and then returns no x-value; `ModAB` leaves the
      limit out, so the evaluation budget ends a long solve, as for every solver.
    - **Unreachable paths, ``"safeguarded_2026"``:** the C# code returns no x-value after a function value that is
      NaN, and its secant returns the midpoint where an ordinate is infinite or both ordinates are 0. `ModAB` leaves
      these paths out, because none of them can occur:

      - `WrappedFunction` raises at a function value that is not finite;
      - scaling only shrinks an ordinate;
      - the ordinate at the bound that moved last is that bound's function value, which is never 0.
    - **Clamping, ``"algorithms_2026"``:** Algorithm 1 evaluates the secant's zero and then clamps it into the
      interval. The C# code clamps first: a secant's zero that rounding puts on or outside a bound is replaced by that
      bound and its stored function value, so nothing is evaluated. In Anderson-Björck mode, such an iteration only
      halves the stored function value at the other bound, or marks the other bound as retained.
    - **The first threshold, ``"algorithms_2026"``:** the paper's section 4.2 sets the threshold at the switch to
      `_FALLBACK_THRESHOLD_FACTOR` times the interval width. Only the C# code shows that this width is measured
      before ``x3`` replaces a bound, where ``x3`` is the x-value whose evaluation triggers the switch.
    - **Arithmetic, ``"safeguarded_2026"``:** the preprint writes the switching test as ``k*(|ym| + |y3|)`` in its
      equation 11, and its section 5.3 guards the secant, the scaling and the switching test against overflow and
      underflow in other ways than the C# code; `ModAB` follows the C# code.

    The method's first version (Ganchovski and Traykov, 2023) is a different algorithm, which the 2026 paper replaces;
    `ModAB` implements only the 2026 versions. The first version differs in 3 ways:

    - it fixes ``k = 0.25``;
    - it falls back to bisection after a fixed number of iterations;
    - it stops once 2 successive x-values lie within the tolerance.

    In an iteration whose ``x3`` lies on a bound, `ModAB` evaluates nothing, so it writes its own loop, not
    `BracketingSolver`'s. Each variant has a loop of its own, which follows the variant's C# code step by step: the 2
    codes differ in almost every step.

    References:
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its Table A1 holds the C# code that
          ``"algorithms_2026"`` ports, and the test suite reproduces its Tables 1 and 2.
          https://doi.org/10.3390/a19050332
        - Tomov, L. and Ganchovski, N. (2026). Global convergence and reliable stopping in a safeguarded modified
          Anderson-Björck method. arXiv preprint 2610.14193 [math.NA], version 1. It describes the method of
          ``"safeguarded_2026"``, and the test suite reproduces its Tables 3 to 5 and the first steps of its
          Proposition 3.6. https://doi.org/10.48550/arXiv.2610.14193
        - ``SgModAB.cs`` at commit ``0d6efd5`` of the authors' repository, the C# code that ``"safeguarded_2026"``
          ports, with the secant ``SafeSecant`` of ``Node.cs``:
          https://github.com/Proektsoft-EOOD/ModAB-Root-Finding/blob/0d6efd59e5dcb34b7bccf90e1d4a9eee6d486e70/MDPI-Algorithms-Data-2/Root/Solvers/SgModAB.cs
          https://github.com/Proektsoft-EOOD/ModAB-Root-Finding/blob/0d6efd59e5dcb34b7bccf90e1d4a9eee6d486e70/MDPI-Algorithms-Data-2/Root/Node.cs
        - Ganchovski, N. and Traykov, A. (2023). Modified Anderson-Björck's method for solving non-linear equations in
          structural mechanics. IOP Conference Series: Materials Science and Engineering 1276, 012010. It
          describes the method's first version. https://doi.org/10.1088/1757-899X/1276/1/012010
        - The authors' repository, https://github.com/Proektsoft-EOOD/ModAB-Root-Finding, which holds the C# code of
          the 2026 paper's supplementary material, and later versions of the method in several languages.
        - pymodab, https://pypi.org/project/pymodab/, a Python wrapper of the authors' compiled C library.
    """

    name = "modab"
    version = 3

    # The 2 constants of "safeguarded_2026", the preprint's B and M, are class attributes, so that the test suite can
    # override them in a subclass to run the other 2 settings of the preprint's Table 3.
    _SAFEGUARDED_FALLBACK_THRESHOLD_FACTOR = 2.0
    _SAFEGUARDED_MAX_RESIDUAL_STEPS = 3

    def __init__(self, *, variant: ModABVariant) -> None:
        """Configure the variant, which may also be given as a plain string; the class docstring describes each variant.

        Raises:
            ValueError: If ``variant`` is not a value of `ModABVariant`.
        """
        self.variant = ModABVariant(variant)

    def _solve(self, state: SolveState) -> float:
        """Run the loop of the variant's C# code, and return the root estimate of `_root_if_converged` or ``x3``."""
        if self.variant is ModABVariant.ALGORITHMS_2026:
            return self._solve_algorithms_2026(state)
        else:
            return self._solve_safeguarded_2026(state)

    # --------------------------------------------------------------------------
    #  The loops of the 2 variants
    # --------------------------------------------------------------------------
    def _solve_algorithms_2026(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with the authors' C# code
        """Run the C# loop of Ganchovski et al. (2026), and return the root estimate of `_root_if_converged` or ``x3``.

        The variables keep the names of the C# code, except for those listed below; the C# code also groups ``x1``
        and ``y1`` into the point ``p1``, and likewise ``p2`` and ``p3``.

        - ``(x_new, y_new)`` is the point that replaces a bound: ``(x3, y3)``, or, when ``x3`` is clamped onto a
          bound, that bound with its stored function value;
        - ``retained_bound`` is the bound that was retained in the last Anderson-Björck step, ``None`` before the first;
          the C# code stores it as the integer ``side``, although the comment on ``side`` calls it the side that moved
          last;
        - ``is_bisecting`` is the mode, ``bisection`` in the C# code.

        Each iteration:

        - computes ``x3``, and ends the solve once `_root_if_converged` returns a root estimate, at the point where the
          C# code tests the interval's width;
        - evaluates ``x3``, unless it is clamped, and in bisection mode tests whether to switch;
        - ends the solve if ``y_new = 0``, and returns ``x3``;
        - replaces a bound by ``(x_new, y_new)``, scaling the retained bound's function value in Anderson-Björck mode;
        - falls back to bisection if the interval is wider than the threshold.
        """
        interval = state.interval
        x1, y1, x2, y2 = interval.a, interval.fa, interval.b, interval.fb
        xtol_doubled = 2.0 * state.xtol
        is_bisecting = True
        retained_bound: IntervalBound | None = None
        threshold = x2 - x1
        while True:
            # --- the new x-value x3 -------------
            if is_bisecting:
                x3 = 0.5 * (x1 + x2)
            else:
                x3 = (x1 * y2 - y1 * x2) / (y2 - y1)
            # The criterion reads the stored values y1 and y2, not f(x1) and f(x2). A stored value is 0 only where
            # scaling a subnormal function value underflows to 0; the solve then ends at that bound.
            x_root = self._root_if_converged(x1, y1, x2, y2, x3, xtol_doubled)
            if x_root is not None:
                return x_root

            # --- the evaluation at x3 -----------
            if is_bisecting:
                y3 = state.f(x3)
                state.x_best = x3
                x_new, y_new = x3, y3
                ym = 0.5 * (y1 + y2)
                r = 1.0 - abs(ym / (y2 - y1))
                k = r * r
                if abs(ym - y3) < k * (abs(y3) + abs(ym)):
                    # The function is close enough to a straight line: switch to Anderson-Björck mode.
                    is_bisecting = False
                    threshold = (x2 - x1) * _FALLBACK_THRESHOLD_FACTOR
            else:
                if x3 <= x1:
                    x_new, y_new = x1, y1
                elif x3 >= x2:
                    x_new, y_new = x2, y2
                else:
                    y3 = state.f(x3)
                    state.x_best = x3
                    x_new, y_new = x3, y3
                threshold = threshold * 0.5
            # A 0 at x3 meets the shared stopping criterion, because x3 then replaces a bound. In a clamped iteration,
            # y_new is a stored value, which the check above found not to be 0.
            if y_new == 0.0:
                return x3

            # --- the new interval ---------------
            # The C# code compares Math.Sign(y_new) with Math.Sign(y1); the test below gives the same result because
            # y_new is not 0 here.
            if (y_new > 0.0 and y1 > 0.0) or (y_new < 0.0 and y1 < 0.0):
                if retained_bound is IntervalBound.UPPER:
                    m = 1.0 - y_new / y1
                    y2 = y2 * (0.5 if m <= 0.0 else m)
                elif not is_bisecting:
                    retained_bound = IntervalBound.UPPER
                x1, y1 = x_new, y_new
            else:
                if retained_bound is IntervalBound.LOWER:
                    m = 1.0 - y_new / y2
                    y1 = y1 * (0.5 if m <= 0.0 else m)
                elif not is_bisecting:
                    retained_bound = IntervalBound.LOWER
                x2, y2 = x_new, y_new
            if x2 - x1 > threshold:
                # The Anderson-Björck steps shrink the interval too slowly: fall back to bisection.
                is_bisecting = True
                retained_bound = None

    def _solve_safeguarded_2026(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with the authors' C# code
        """Run the loop of ``SgModAB.cs``, and return the root estimate of `_root_if_converged` or ``x3``.

        ``y1`` and ``y2`` are always the function values at the bounds, and ``f1`` and ``f2`` the ordinates that the
        Anderson-Björck steps scale. The variables keep the names of the C# code, except for those listed below; the
        C# code also groups ``x1`` and ``y1`` into the node ``p1``, and likewise ``p2`` and ``p3``.

        - ``moved_bound`` is the bound that the last Anderson-Björck step replaced, ``None`` at the start of each
          Anderson-Björck phase; the C# code stores it as the integer ``sideMoved``;
        - ``is_switching_to_ab`` is ``switchToAB`` in the C# code;
        - `_SAFEGUARDED_FALLBACK_THRESHOLD_FACTOR` and `_SAFEGUARDED_MAX_RESIDUAL_STEPS` are ``C`` and
          ``MaxResidualSteps``.

        Each iteration:

        - computes ``x3``, projected into the interval in Anderson-Björck mode, and ends the solve once
          `_root_if_converged` returns a root estimate, at the point where the C# code tests the interval's width;
        - evaluates ``x3``, unless it lies on a bound, whose function value it then reuses;
        - ends the solve if ``y3 = 0``, and returns ``x3``;
        - in Anderson-Björck mode, records the smaller of ``|y1|`` and ``|y2|``, replaces a bound by ``(x3, y3)``,
          scales the retained bound's ordinate ``f1`` or ``f2``, and falls back to bisection if the interval is wider
          than the threshold, unless it grants a residual exception;
        - in bisection mode, tests whether to switch, replaces a bound by ``(x3, y3)``, and then switches, setting the
          threshold from the new interval's width and the ordinates ``f1`` and ``f2`` to ``y1`` and ``y2``.
        """
        interval = state.interval
        x1, y1, x2, y2 = interval.a, interval.fa, interval.b, interval.fb
        xtol_doubled = 2.0 * state.xtol
        f1 = f2 = 0.0
        is_ab = False
        moved_bound: IntervalBound | None = None
        fallback_threshold = 0.0
        y_min = 0.0
        residual_steps = 0
        while True:
            # --- the new x-value x3 -------------
            if is_ab:
                x3 = self._safe_secant_zero(x1, f1, x2, f2)
            else:
                x3 = 0.5 * x1 + 0.5 * x2
            # The criterion reads the function values y1 and y2, which are never 0 here.
            x_root = self._root_if_converged(x1, y1, x2, y2, x3, xtol_doubled)
            if x_root is not None:
                return x_root

            # --- the evaluation at x3 -----------
            # An x3 on a bound reuses the function value there, so nothing is evaluated.
            if x3 == x1:
                y3 = y1
            elif x3 == x2:
                y3 = y2
            else:
                y3 = state.f(x3)
                state.x_best = x3
            # A 0 at x3 meets the shared stopping criterion, because x3 then replaces a bound. A reused value is the
            # function value at a bound, which is never 0.
            if y3 == 0.0:
                return x3
            is_switching_to_ab = False
            if is_ab:
                # The fallback rule compares |y3| with half the smaller |y| at the bounds before the update.
                y_min = min(abs(y1), abs(y2))
            else:
                # The C# code computes y2 - y1 twice; computing it once gives the same value. The C# code skips the
                # test where it overflows.
                y2_minus_y1 = y2 - y1
                if math.isfinite(y2_minus_y1):
                    ym = 0.5 * (y1 + y2)
                    r = 1.0 - abs(ym / y2_minus_y1)
                    k = r * r
                    is_switching_to_ab = abs(ym - y3) < k * abs(ym) + k * abs(y3)

            # --- the new interval ---------------
            # The C# code tests SameSign(y1, y3), as the tests below do: y1 and y3 are not 0 here.
            if is_ab:
                if (y3 > 0.0 and y1 > 0.0) or (y3 < 0.0 and y1 < 0.0):
                    if moved_bound is IntervalBound.LOWER:
                        m = 1.0 - y3 / f1
                        f2 = f2 * (m if m > 0.0 else 0.5)
                    else:
                        moved_bound = IntervalBound.LOWER
                    x1, y1, f1 = x3, y3, y3
                else:
                    if moved_bound is IntervalBound.UPPER:
                        m = 1.0 - y3 / f2
                        f1 = f1 * (m if m > 0.0 else 0.5)
                    else:
                        moved_bound = IntervalBound.UPPER
                    x2, y2, f2 = x3, y3, y3
                if x2 - x1 > fallback_threshold:
                    # The interval shrinks too slowly. A residual exception continues the phase if |y3| is below
                    # half of y_min, at most _SAFEGUARDED_MAX_RESIDUAL_STEPS times in a row; otherwise, the solve
                    # falls back to bisection.
                    if residual_steps >= self._SAFEGUARDED_MAX_RESIDUAL_STEPS or abs(y3) >= 0.5 * y_min:
                        is_ab = False
                        moved_bound = None
                    else:
                        residual_steps += 1
                else:
                    residual_steps = 0
                fallback_threshold = fallback_threshold * 0.5
            else:
                if (y3 > 0.0 and y1 > 0.0) or (y3 < 0.0 and y1 < 0.0):
                    x1, y1 = x3, y3
                else:
                    x2, y2 = x3, y3
                if is_switching_to_ab:
                    # The function is close enough to a straight line: switch to Anderson-Björck mode.
                    is_ab = True
                    residual_steps = 0
                    fallback_threshold = self._SAFEGUARDED_FALLBACK_THRESHOLD_FACTOR * (x2 - x1)
                    f1, f2 = y1, y2

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _safe_secant_zero(x1: float, y1: float, x2: float, y2: float) -> float:
        """Return the zero of the secant through ``(x1, y1)`` and ``(x2, y2)``, projected into ``[x1, x2]``.

        The method computes the zero as the C# code of ``"safeguarded_2026"`` does in ``SafeSecant``, in a weighted
        form whose 2 weights lie in ``[0, 1]``. ``y1`` and ``y2`` are finite, with opposite signs, or 1 of them is 0.
        Where ``|y1| + |y2|`` overflows, halving both magnitudes makes the sum finite and keeps the weights.
        """
        a = abs(y1)
        b = abs(y2)
        den = a + b
        if math.isinf(den):
            a = a * 0.5
            b = b * 0.5
            den = a + b
        w1 = b / den
        w2 = a / den
        return min(max(w1 * x1 + w2 * x2, x1), x2)

    @staticmethod
    def _root_if_converged(x1: float, y1: float, x2: float, y2: float, x3: float, xtol_doubled: float) -> float | None:
        """Return the root estimate if the solve ends before evaluating ``x3``, or ``None`` if it continues.

        ``x3`` is not used. The test suite overrides this method to apply the C# code's own stopping criterion, the
        interval at most ``aTol + rTol*|x3|`` wide, where it reproduces the papers' published counts.
        """
        return interval_root_if_converged(x1, y1, x2, y2, xtol_doubled)
