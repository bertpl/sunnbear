"""`ITP` implements the ITP method: interpolation, truncated toward the midpoint and projected around it."""

import math

from sunnbear._core.solvers.core import BracketingSolver, Interval

from .state import ITPState


class ITP(BracketingSolver[ITPState]):
    """`ITP` implements the ITP method as the pseudocode in Appendix B of its paper states it.

    The paper is Oliveira and Takahashi, ACM Transactions on Mathematical Software 47(1), article 5. Each iteration
    evaluates 1 point, ``x_itp``, which it computes from the interval ``[a, b]`` and its midpoint ``x_half`` in 3
    steps:

    - interpolation: ``x_f`` is where the chord through ``(a, f(a))`` and ``(b, f(b))`` crosses zero, as in regula
      falsi;
    - truncation: ``x_t`` is ``x_f`` moved toward ``x_half`` by ``delta = kappa_1 * (b - a)^kappa_2``, or
      ``x_half`` itself when ``x_f`` lies closer to ``x_half`` than ``delta``;
    - projection: ``x_itp`` is ``x_t``, or, when ``x_t`` lies farther than a radius ``r`` from ``x_half``, the point
      at distance ``r`` from ``x_half`` toward ``x_t``; the next paragraph defines ``r``.

    In iteration ``k``, counted from 0, the radius ``r = xtol * 2^(n_max - k) - (b - a) / 2`` keeps the solve within
    ``n_max = n_bisection + n_slack`` iterations.

    Here ``n_bisection = ceil(log2((b0 - a0) / (2 * xtol)))``, the paper's ``n_1/2``, is the iteration count of
    bisection on the initial interval ``[a0, b0]``. So, in exact arithmetic, the method needs at most ``n_slack``
    iterations more than bisection, while it converges superlinearly on smooth functions. In floating point, rounding
    errors can push a solve 1 or more iterations past ``n_max``.

    The constants follow the paper's experiments: ``kappa_2 = 2``, and ``kappa_1 = 0.2 / (b0 - a0)``, so that the
    first truncation moves ``x_f`` by at most 20 % of the initial width.

    ``is_robust`` replaces ``r`` with ``max(0.99 * r - xtol / 2, 0)``, the correction for rounding errors that the
    authors' MATLAB code applies and that the paper's Appendix B recommends in general terms. It reduces the solves
    that go past ``n_max``, but does not prevent them all.

    The interval, the stopping criterion and the root estimate are `BracketingSolver`'s: the solve ends once the
    interval is at most ``2 * xtol`` wide, as in the paper, and returns its midpoint.
    """

    name = "itp"
    version = 1
    state_cls = ITPState

    # `_KAPPA_2` is the paper's kappa_2; kappa_1 depends on the initial interval, so `_solve` sets it per solve.
    _KAPPA_2 = 2

    def __init__(self, *, n_slack: int, is_robust: bool) -> None:
        """Configure the method.

        Args:
            n_slack: The paper's ``n_0``, the number of iterations that the solve may take beyond the iteration count
                of bisection.
            is_robust: Whether ``r`` gets the correction for rounding errors that the authors' MATLAB code applies.

        Raises:
            ValueError: If ``n_slack`` is negative.
        """
        if n_slack < 0:
            raise ValueError(f"n_slack must be at least 0 (got {n_slack}).")
        self.n_slack = n_slack
        self.is_robust = is_robust

    def _solve(self, state: ITPState) -> float:
        """Set the solve's ``kappa_1`` and first ``max_next_width`` on ``state``, then run `BracketingSolver`'s loop.

        The paper computes ``xtol * 2^(n_max - k)`` in every iteration; `ITP` computes it once and halves it every
        iteration, which gives the same values exactly.
        """
        width = state.interval.width
        n_bisection = math.ceil(math.log2(width / (2.0 * state.xtol)))
        state.kappa_1 = 0.2 / width
        state.max_next_width = state.xtol * 2.0 ** (n_bisection + self.n_slack)
        return super()._solve(state)

    def _next_x(self, state: ITPState, interval: Interval) -> float:
        """Return ``x_itp``: the interpolation point ``x_f``, truncated and projected as the class docstring says."""
        # --- interpolation ----------------------
        x_f = (interval.fb * interval.a - interval.fa * interval.b) / (interval.fb - interval.fa)

        # --- truncation -------------------------
        x_half = interval.midpoint
        x_half_minus_x_f = x_half - x_f
        if x_half_minus_x_f > 0.0:
            sigma = 1.0
        elif x_half_minus_x_f < 0.0:
            sigma = -1.0
        else:
            sigma = 0.0
        delta = state.kappa_1 * interval.width**self._KAPPA_2
        if delta <= abs(x_half_minus_x_f):
            x_t = x_f + sigma * delta
        else:
            x_t = x_half

        # --- projection -------------------------
        r = state.max_next_width - 0.5 * interval.width
        state.max_next_width = 0.5 * state.max_next_width
        if self.is_robust:
            r = max(0.99 * r - 0.5 * state.xtol, 0.0)
        if abs(x_t - x_half) <= r:
            return x_t
        else:
            return x_half - sigma * r
