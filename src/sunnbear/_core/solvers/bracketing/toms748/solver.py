"""`TOMS748` implements Algorithm 748: interpolation steps, a double-size secant step, and bisection if needed."""

import sys

from sunnbear._core.solvers.core import Interval, IntervalBound, Solver, SolveState

# ``_MACHEPS`` is the paper's ``macheps``, the relative machine precision: 2^-52 for float64.
_MACHEPS = sys.float_info.epsilon

# ``_MU`` is the paper's ``mu``: an iteration that leaves the interval wider than ``_MU`` times its width at the start
# of the iteration ends with a bisection.
_MU = 0.5

# ``_LAMBDA`` is the paper's ``lambda``: `_evaluate_and_split_at` uses it to keep each new point away from the bounds of
# the interval.
_LAMBDA = 0.7

# The authors' code starts ``e`` and ``f(e)`` at this value, which no step reads. ``e`` is the bound discarded before
# the most recently discarded one; the only step that runs before ``e`` is set, the first interpolation step of the
# second iteration, always takes Newton steps, which do not read ``e``.
_UNSET = 1.0e5


class TOMS748(Solver):
    """`TOMS748` implements Algorithm 748 (Alefeld, Potra and Shi, 1995), with ``k`` interpolation steps per iteration.

    The first iteration takes a secant step. Each later iteration evaluates the function at 1 point per step:

    - ``k`` interpolation steps. The j-th step, counted from 1, takes the zero of the inverse cubic interpolation
      through the bounds ``a`` and ``b`` and the 2 most recently discarded bounds, ``d`` and ``e``. When the 4
      function values are not distinct, or when that zero lies outside ``(a, b)``, it takes ``j + 1`` Newton steps
      on the quadratic through ``a``, ``b`` and ``d``. The first step of the second iteration always takes the
      Newton steps, because ``e`` is not known yet.
    - a double-size secant step: from ``u``, the bound with the smaller ``|f|``, a step twice as long as the secant
      step; when that step would be longer than half the interval, the midpoint instead.
    - a bisection, unless the interval has shrunk below half its width at the start of the iteration.

    ``k = 1`` is the paper's Algorithm 4.1 and ``k = 2`` its Algorithm 4.2.

    The paper states the 2 algorithms without a stopping criterion; its experiments, and the authors' code, add the
    stopping criterion of Brent's method:

    - ``stop_width = 2 * (2 * macheps * |u| + tol)``, with ``macheps`` the relative machine precision and ``tol`` an
      absolute tolerance that the solver derives from ``xtol``;
    - the solve ends once the interval is at most ``stop_width`` wide, or once an evaluation returns exactly 0, and
      returns the lower bound ``a``, or the point that returned 0.

    The experiments and the code also keep every new point at least ``0.7 * stop_width`` inside the interval, and
    take the midpoint when the interval is at most ``1.4 * stop_width`` wide.

    The returned ``a`` lies within ``stop_width`` of a root. The solver sets
    ``tol = xtol / 2 - 2 * macheps * max(|a0|, |b0|)``, with ``a0`` and ``b0`` the bounds of the initial interval, so
    that ``stop_width`` never exceeds ``xtol``.

    Where ``xtol`` is below ``4 * macheps * max(|a0|, |b0|)``, ``tol`` would be negative and the margin of 0.7 times
    ``stop_width`` could move a point outside the interval; the solver then sets ``tol = 0``, the setting of the
    authors' test runs, and the accuracy of ``xtol`` is no longer guaranteed.

    `BracketingSolver`'s loop evaluates the function once per iteration, and an iteration of `TOMS748` evaluates it up
    to ``k + 2`` times, so `TOMS748` writes its own loop.

    References:
        - Alefeld, G. E., Potra, F. A. and Shi, Y. (1995). Algorithm 748: Enclosing zeros of continuous functions.
          ACM Transactions on Mathematical Software 21(3), 327-344. Its subroutine ``ipzero`` is the inverse cubic
          interpolation, and its section 6 states the stopping criterion and the margin.
          https://doi.org/10.1145/210089.210111
        - The authors' Fortran 77 code, published with the paper as algorithm 748 of the Collected Algorithms of the
          ACM (netlib, ``toms/748``). It implements Algorithm 4.2, which ``k = 2`` follows line by line, and the test
          suite reproduces the roots that the code lists for its test problems.
    """

    name = "toms748"
    version = 1

    def __init__(self, *, k: int) -> None:
        """Configure the number ``k`` of interpolation steps per iteration.

        ``k = 1`` and ``k = 2`` are the paper's Algorithms 4.1 and 4.2.

        Raises:
            ValueError: If ``k`` is not 1 or 2.
        """
        if k not in (1, 2):
            raise ValueError(f"k must be 1 or 2 (got {k}).")
        self.k = k

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — the loop follows the authors' code step by step
        """Run Algorithm 4.1 or 4.2 and return the lower bound of the final interval.

        The variables keep the names of the paper and the authors' code, so that this method can be compared with the
        paper and the authors' code step by step:

        - ``interval`` is the enclosing interval ``[a, b]``, with ``f(a)`` and ``f(b)`` of opposite signs;
        - ``d`` is the bound that the last call of `_evaluate_and_split_at` discarded, and ``e`` the value of ``d``
          before that call; both lie outside the interval, and ``fd`` and ``fe`` are their function values;
        - ``c`` is the point to evaluate next.

        Each call of `_evaluate_and_split_at` evaluates 1 point and returns the new interval; the solve ends after any
        call that returns an interval with ``f(a) = 0``, or one at most ``stop_width`` wide. A midpoint is computed as
        ``a + 0.5 * (b - a)``, as in the authors' code, not with `Interval.midpoint`, which rounds differently.
        """
        interval = state.interval
        tol = self._get_tol(state.xtol, interval.a, interval.b)
        # The first call of _evaluate_and_split_at sets d and fd before any step reads them.
        d = fd = e = fe = _UNSET
        n_iterations = 0
        while True:
            iteration_start_width = interval.width
            n_iterations += 1
            stop_width = self._get_stop_width(interval, tol)
            if interval.width <= stop_width:
                return interval.a

            # --- iteration 1: the secant step ---
            if n_iterations == 1:
                c = interval.a - (interval.fa / (interval.fb - interval.fa)) * interval.width
                interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
                if interval.is_fa_zero or interval.width <= stop_width:
                    return interval.a
                continue

            # --- the k interpolation steps ------
            for j in range(1, self.k + 1):
                a, b, fa, fb = interval.a, interval.b, interval.fa, interval.fb
                # The product is 0 exactly when 2 of the 4 function values are equal.
                product_of_f_differences = (fa - fb) * (fa - fd) * (fa - fe) * (fb - fd) * (fb - fe) * (fd - fe)
                if (j == 1 and n_iterations == 2) or product_of_f_differences == 0.0:
                    c = self._newton_quadratic_zero(a, b, d, fa, fb, fd, j + 1)
                else:
                    c = self._inverse_cubic_zero(a, b, d, e, fa, fb, fd, fe)
                    if (c - a) * (c - b) >= 0.0:
                        c = self._newton_quadratic_zero(a, b, d, fa, fb, fd, j + 1)
                if j < self.k:
                    # The next interpolation step uses this step's d as its e.
                    e, fe = d, fd
                interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
                if interval.is_fa_zero or interval.width <= stop_width:
                    return interval.a
            e, fe = d, fd

            # --- the double-size secant step ----
            u, fu = self._get_u(interval)
            c = u - 2.0 * (fu / (interval.fb - interval.fa)) * interval.width
            if abs(c - u) > 0.5 * interval.width:
                c = interval.a + 0.5 * interval.width
            interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
            if interval.is_fa_zero or interval.width <= stop_width:
                return interval.a

            # --- the bisection, if needed -------
            if interval.width < _MU * iteration_start_width:
                continue
            e, fe = d, fd
            c = interval.a + 0.5 * interval.width
            interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
            if interval.is_fa_zero or interval.width <= stop_width:
                return interval.a

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _get_tol(xtol: float, a0: float, b0: float) -> float:
        """Return the ``tol`` that keeps ``stop_width`` at most ``xtol``, or 0 where that ``tol`` would be negative."""
        return max(0.5 * xtol - 2.0 * _MACHEPS * max(abs(a0), abs(b0)), 0.0)

    @staticmethod
    def _get_u(interval: Interval) -> tuple[float, float]:
        """Return ``u``, the bound with the smaller ``|f|``, and ``b`` when both are equal, with ``f(u)``."""
        if abs(interval.fb) <= abs(interval.fa):
            return interval.b, interval.fb
        else:
            return interval.a, interval.fa

    @staticmethod
    def _get_stop_width(interval: Interval, tol: float) -> float:
        """Return ``stop_width = 2 * (2 * macheps * |u| + tol)`` for ``interval``, the authors' subroutine ``TOLE``."""
        u, _ = TOMS748._get_u(interval)
        return 2.0 * (tol + 2.0 * abs(u) * _MACHEPS)

    def _evaluate_and_split_at(
        self, state: SolveState, interval: Interval, c: float, stop_width: float, tol: float
    ) -> tuple[Interval, float, float, float]:
        """Evaluate ``c`` and return the interval that still holds the sign change: the authors' subroutine ``BRACKT``.

        Before the evaluation, ``c`` is moved to at least ``_LAMBDA * stop_width`` inside the interval, or to the
        midpoint when the interval is at most ``2 * _LAMBDA * stop_width`` wide. The method also sets
        ``state.x_best`` to the lower bound of the new interval.

        Returns:
            A tuple of:

            - the new interval; if ``f(c)`` is exactly 0, it is ``[c, b]`` with ``f(a) = 0``;
            - the discarded bound ``d``;
            - ``f(d)``;
            - the ``stop_width`` of the new interval.
        """
        margin = _LAMBDA * stop_width
        if interval.width <= 2.0 * margin:
            c = interval.a + 0.5 * interval.width
        elif c <= interval.a + margin:
            c = interval.a + margin
        elif c >= interval.b - margin:
            c = interval.b - margin
        fc = state.f(c)
        # split_at treats a zero f(c) as having the sign of f(a), so it replaces a with c.
        new_interval = interval.split_at(c, fc)
        if new_interval.last_replaced_bound is IntervalBound.LOWER:
            d, fd = interval.a, interval.fa
        else:
            d, fd = interval.b, interval.fb
        state.x_best = new_interval.a
        return new_interval, d, fd, self._get_stop_width(new_interval, tol)

    @staticmethod
    def _newton_quadratic_zero(a: float, b: float, d: float, fa: float, fb: float, fd: float, n_steps: int) -> float:
        """Return the zero in ``(a, b)`` of the quadratic through ``a``, ``b`` and ``d``, by ``n_steps`` Newton steps.

        This is the paper's subroutine Newton-Quadratic, as the authors' subroutine ``NEWQUA`` implements it.

        The quadratic is ``p(x) = fa + a1 * (x - a) + a2 * (x - a) * (x - b)``, with the divided differences
        ``a1 = f[a, b]`` and ``a2 = f[a, b, d]``. The Newton steps start from the bound where ``p`` has the same sign
        as ``p'' = 2 * a2``; from that bound, each step moves toward the zero without passing it.

        When ``a2 = 0``, or when a step meets ``p'(x) = 0``, the zero of the line ``fa + a1 * (x - a)`` is returned.
        """
        a1 = (fb - fa) / (b - a)
        a2 = ((fd - fb) / (d - b) - a1) / (d - a)
        if a2 == 0.0:
            return a - fa / a1
        else:
            if (a2 > 0.0) == (fa > 0.0):
                c = a
            else:
                c = b
            for _ in range(n_steps):
                pc = fa + (a1 + a2 * (c - b)) * (c - a)
                pdc = a1 + a2 * ((2.0 * c) - (a + b))
                if pdc == 0.0:
                    return a - fa / a1
                c = c - pc / pdc
            return c

    @staticmethod
    def _inverse_cubic_zero(
        a: float, b: float, d: float, e: float, fa: float, fb: float, fd: float, fe: float
    ) -> float:
        """Return the zero of the inverse cubic interpolation through ``a``, ``b``, ``d`` and ``e``.

        This is the paper's subroutine ``ipzero``, the authors' subroutine ``PZERO``: an Aitken-Neville scheme for the
        value at ``y = 0`` of the cubic ``x(y)`` through the 4 points ``(f(x), x)``. The 4 function values must be
        distinct.
        """
        q11 = (d - e) * fd / (fe - fd)
        q21 = (b - d) * fb / (fd - fb)
        q31 = (a - b) * fa / (fb - fa)
        d21 = (b - d) * fd / (fd - fb)
        d31 = (a - b) * fb / (fb - fa)
        q22 = (d21 - q11) * fb / (fe - fb)
        q32 = (d31 - q21) * fa / (fd - fa)
        d32 = (d31 - q21) * fd / (fd - fa)
        q33 = (d32 - q22) * fa / (fe - fa)
        return a + (q31 + q32 + q33)
