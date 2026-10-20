"""`ModABSafeguarded` implements the safeguarded modified Anderson-Björck method of Tomov and Ganchovski (2026)."""

# `ModABSafeguarded` is ported from C# code under the MIT license, © 2026 Ned Ganchovski; THIRD_PARTY_NOTICES.md holds
# that code's copyright and license notice.

import math

from sunnbear._core.solvers.core import IntervalBound, Solver, SolveState
from sunnbear._core.solvers.core.stopping import interval_root_if_converged


class ModABSafeguarded(Solver):
    """`ModABSafeguarded` ports the safeguarded modified Anderson-Björck method from the authors' ``SgModAB.cs``.

    The method is that of `ModAB` with 4 changes; the class docstring of `ModAB` describes its 2 modes, bisection and
    Anderson-Björck. Tomov and Ganchovski (2026) find 2 defects in the C# code of `ModAB`, which the changes *No
    scaling in the first Anderson-Björck step* and *True function values kept apart* correct:

    - **No scaling in the first Anderson-Björck step:** in `ModAB`, the bisection step that switches already counts as
      the first of 2 iterations in a row that retain a bound, so a first Anderson-Björck step that retains the same
      bound scales that bound's stored function value. `ModABSafeguarded` starts each Anderson-Björck phase, the
      sequence of Anderson-Björck steps from a switch to the next fallback, with no record of which bound the previous
      step replaced.
    - **True function values kept apart:** `ModABSafeguarded` scales copies of ``y1`` and ``y2``, the ordinates
      ``f1`` and ``f2``, which only the secant reads, and resets the ordinates to ``y1`` and ``y2`` at each switch. In
      `ModAB`, as its C# code shows, a scaled value replaces the stored function value, and stays stored after a
      fallback to bisection, where the switching test reads it.
    - **Fallback rule:** the switch sets the threshold to `_FALLBACK_THRESHOLD_FACTOR` times the interval width after
      ``x3`` replaces a bound. An Anderson-Björck step that leaves the interval wider than the threshold still continues
      the phase, as a residual exception, if ``|y3|`` is below half the smaller of ``|y1|`` and ``|y2|`` before the
      step; at most `_MAX_RESIDUAL_STEPS` steps in a row may be residual exceptions.
    - **Forms of the steps:** the secant's zero is ``(b/den)*x1 + (a/den)*x2``, projected into the interval, where
      ``a`` and ``b`` are the magnitudes of the ordinates at ``x1`` and ``x2``, and ``den = a + b``; where ``den``
      overflows, ``a`` and ``b`` are halved first. The midpoint is ``0.5*x1 + 0.5*x2``. The switching test is
      ``|ym - y3| < k*|ym| + k*|y3|``, and is skipped where ``y2 - y1`` overflows.

    The solve checks the shared stopping criterion at the 2 points of each iteration where the C# code checks its own:

    - after computing ``x3`` and before evaluating it, the solve ends once the interval is at most ``2*xtol`` wide, and
      returns the interval's midpoint, which then lies within ``xtol`` of a root;
    - after evaluating ``x3``, the solve ends once ``y3 = 0``, and returns ``x3``.

    `ModABSafeguarded` follows the C# code where the preprint differs from it or leaves a detail out, and departs from
    the C# code in its stopping criterion, its iteration limit, and code paths that can never run in sunnbear:

    - **Stopping criterion:** before evaluating ``x3``, the C# code ends the solve once the interval is at most
      ``aTol + rTol*|x3|`` wide, for an absolute tolerance ``aTol`` and a relative tolerance ``rTol``, and returns
      ``x3``, not the interval's midpoint.
    - **No iteration limit:** the C# code stops after 200 iterations and then returns no x-value; `ModABSafeguarded`
      leaves the limit out, so the evaluation budget ends a long solve, as for every solver.
    - **Unreachable paths:** the C# code returns no x-value after a function value that is NaN, and its secant returns
      the midpoint where an ordinate is infinite or both ordinates are 0. `ModABSafeguarded` leaves these paths out,
      because none of them can occur:

      - `WrappedFunction` raises at a function value that is not finite;
      - scaling only shrinks an ordinate;
      - the ordinate at the bound that moved last is that bound's function value, which is never 0.
    - **Arithmetic:** the preprint writes the switching test as ``k*(|ym| + |y3|)`` in its equation 11, and its section
      5.3 guards the secant, the scaling and the switching test against overflow and underflow in other ways than the
      C# code; `ModABSafeguarded` follows the C# code.

    In an iteration whose ``x3`` lies on a bound, `ModABSafeguarded` evaluates nothing, so it writes its own loop, not
    `BracketingSolver`'s.

    References:
        - Tomov, L. and Ganchovski, N. (2026). Global convergence and reliable stopping in a safeguarded modified
          Anderson-Björck method. arXiv preprint 2610.14193 [math.NA], version 1. It describes the method, and the test
          suite reproduces its Tables 3 to 5 and the first steps of its Proposition 3.6.
          https://doi.org/10.48550/arXiv.2610.14193
        - ``SgModAB.cs`` at commit ``0d6efd5`` of the authors' repository, the C# code that `ModABSafeguarded` ports,
          with the secant ``SafeSecant`` of ``Node.cs``:
          https://github.com/Proektsoft-EOOD/ModAB-Root-Finding/blob/0d6efd59e5dcb34b7bccf90e1d4a9eee6d486e70/MDPI-Algorithms-Data-2/Root/Solvers/SgModAB.cs
          https://github.com/Proektsoft-EOOD/ModAB-Root-Finding/blob/0d6efd59e5dcb34b7bccf90e1d4a9eee6d486e70/MDPI-Algorithms-Data-2/Root/Node.cs
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. It describes the method that
          `ModABSafeguarded` corrects, which `ModAB` implements. https://doi.org/10.3390/a19050332
    """

    name = "modab_safeguarded"
    version = 1

    # The method's 2 constants, the preprint's B and M, are class attributes, so that the test suite can override them
    # in a subclass to run the other 2 settings of the preprint's Table 3.
    _FALLBACK_THRESHOLD_FACTOR = 2.0
    _MAX_RESIDUAL_STEPS = 3

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with the authors' C# code
        """Run the loop of ``SgModAB.cs``, and return the root estimate of `_root_if_converged` or ``x3``.

        ``y1`` and ``y2`` are always the function values at the bounds, and ``f1`` and ``f2`` the ordinates that the
        Anderson-Björck steps scale. The variables keep the names of the C# code, except for those listed below; the
        C# code also groups ``x1`` and ``y1`` into the node ``p1``, and likewise ``p2`` and ``p3``.

        - ``moved_bound`` is the bound that the last Anderson-Björck step replaced, ``None`` at the start of each
          Anderson-Björck phase; the C# code stores it as the integer ``sideMoved``;
        - ``is_switching_to_ab`` is ``switchToAB`` in the C# code;
        - `_FALLBACK_THRESHOLD_FACTOR` and `_MAX_RESIDUAL_STEPS` are ``C`` and ``MaxResidualSteps``.

        Each iteration:

        - computes ``x3``, projected into the interval in Anderson-Björck mode, and ends the solve once
          `_root_if_converged` returns a root estimate, at the point where the C# code tests the interval's width;
        - evaluates ``x3``, or, where ``x3`` lies on a bound, reuses that bound's function value;
        - ends the solve if ``y3 = 0``, and returns ``x3``;
        - in Anderson-Björck mode, records the smaller of ``|y1|`` and ``|y2|``, replaces a bound by ``(x3, y3)``,
          scales the retained bound's ordinate ``f1`` or ``f2``, and falls back to bisection if the interval is wider
          than the threshold, unless the step is granted a residual exception;
        - in bisection mode, tests whether to switch, replaces a bound by ``(x3, y3)``, and switches if the test passed,
          setting the threshold from the new interval's width and the ordinates ``f1`` and ``f2`` to ``y1`` and ``y2``.
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
                # The C# code computes y2 - y1 twice; computing it once gives the same value.
                y2_minus_y1 = y2 - y1
                if math.isfinite(y2_minus_y1):
                    ym = 0.5 * (y1 + y2)
                    r = 1.0 - abs(ym / y2_minus_y1)
                    k = r * r
                    is_switching_to_ab = abs(ym - y3) < k * abs(ym) + k * abs(y3)

            # --- the new interval ---------------
            # The C# code tests SameSign(y1, y3); the sign comparisons below are equivalent, because y1 and y3 are
            # not 0 here.
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
                    # The interval shrinks too slowly: fall back to bisection, unless the step is granted a residual
                    # exception.
                    if residual_steps >= self._MAX_RESIDUAL_STEPS or abs(y3) >= 0.5 * y_min:
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
                    fallback_threshold = self._FALLBACK_THRESHOLD_FACTOR * (x2 - x1)
                    f1, f2 = y1, y2

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _safe_secant_zero(x1: float, y1: float, x2: float, y2: float) -> float:
        """Return the zero of the secant through ``(x1, y1)`` and ``(x2, y2)``, projected into ``[x1, x2]``.

        `_safe_secant_zero` computes the zero as the C# code does in ``SafeSecant``, in a weighted form whose 2 weights
        lie in ``[0, 1]``. ``y1`` and ``y2`` are finite, with opposite signs, or 1 of them is 0. Where ``|y1| + |y2|``
        overflows, halving both magnitudes makes the sum finite and keeps the weights.
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

        ``x3`` is not used here. The test suite overrides this method to apply the C# code's own stopping criterion,
        which ends the solve once the interval is at most ``aTol + rTol*|x3|`` wide; with that criterion, the solver
        reproduces the preprint's published counts.
        """
        return interval_root_if_converged(x1, y1, x2, y2, xtol_doubled)
