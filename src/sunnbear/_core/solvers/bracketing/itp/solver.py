"""`ITP` implements the ITP method: interpolation, truncated toward the midpoint and projected around it."""

import math

from sunnbear._core.solvers.core import BracketingSolver, Interval

from .state import ITPState
from .variant import ITPVariant

# ``kappa_1`` and ``kappa_2`` are the constants of the truncation step in the `ITP` docstring, with the values of the
# experiments of Oliveira and Takahashi (2020). ``kappa_1`` depends on the initial interval, so `ITP._solve` sets it
# per solve from `_KAPPA_1_TIMES_INITIAL_WIDTH`.
_KAPPA_1_TIMES_INITIAL_WIDTH = 0.2
_KAPPA_2 = 2


class ITP(BracketingSolver[ITPState]):
    """`ITP` implements the ITP method, in the variant of its paper's pseudocode or in that of its paper's experiments.

    The paper is Oliveira and Takahashi (2020). Each iteration evaluates 1 point, ``x_itp``, which it computes from
    the interval ``[a, b]`` and its midpoint ``x_half`` in 3 steps:

    - interpolation: ``x_f`` is where the chord through ``(a, f(a))`` and ``(b, f(b))`` crosses zero, as in regula
      falsi;
    - truncation: ``x_t`` is ``x_f`` moved toward ``x_half`` by ``delta = kappa_1 * (b - a)^kappa_2``, for 2
      constants ``kappa_1`` and ``kappa_2``, or ``x_half`` itself when ``x_f`` lies closer to ``x_half`` than
      ``delta``;
    - projection: ``x_itp`` is ``x_t``, or, when ``x_t`` lies farther than a radius ``r`` from ``x_half``, the point
      at distance ``r`` from ``x_half`` toward ``x_t``; the projection radius ``r`` is defined after this list.

    ``n_bisection = ceil(log2((b0 - a0) / (2 * xtol)))``, the paper's ``n_1/2``, is the iteration count of bisection
    on the initial interval ``[a0, b0]``.

    In iteration ``k``, counted from 0, the radius ``r = xtol * 2^(n_max - k) - (b - a) / 2`` keeps the solve within
    ``n_max = n_bisection + n_slack`` iterations.

    So, in exact arithmetic, the method needs at most ``n_slack`` iterations more than bisection, while it converges
    superlinearly on smooth functions. In floating point, once the interval nears the width that ``n_max`` allows,
    rounding errors in the bounds can leave it slightly wider than ``2 * xtol`` after iteration ``n_max``, so 1 or
    more iterations follow; this holds for every ``n_slack``.

    The constants follow the paper's experiments: ``kappa_2 = 2``, and ``kappa_1 = 0.2 / (b0 - a0)``, so that the
    first truncation moves ``x_f`` by at most 20 % of the initial width.

    ``variant``, a value of `ITPVariant`, picks the projection radius ``r``, from 1 of 2 sources in the paper:

    - ``"paper_pseudocode"``: ``r`` as the pseudocode of the paper's Appendix B states it.
    - ``"paper_experiments"``: ``r`` becomes ``max(0.99 * r - xtol / 2, 0)``, as in the authors' MATLAB code that
      produced the paper's experiments.

    ``"paper_experiments"`` comes much closer to the iteration counts of the paper's Table 1 than
    ``"paper_pseudocode"``: it matches 23 of the 24 rows, and differs by 1 iteration on the step function, as a
    line-by-line port of the authors' MATLAB code does too.

    The margin, the amount by which ``"paper_experiments"`` lowers ``r``, has 2 effects:

    - it guards against rounding errors in ``r``, as the paper's Appendix B recommends in general terms; the margin
      makes solves that go past ``n_max`` rarer, but does not prevent them all;
    - it keeps each step at most ``0.99 * r - xtol / 2`` from ``x_half``, so ``r`` stays above 0, and interpolation
      steps are accepted again once the interval has shrunk. Under ``"paper_pseudocode"``, once a step lands at
      distance ``r`` from ``x_half``, ``r`` becomes 0 and stays 0, so every later step is the midpoint ``x_half``.

    The interval, the stopping criterion and the root estimate are `BracketingSolver`'s: the solve ends once the
    interval is at most ``2 * xtol`` wide, as in the paper, and returns its midpoint.

    References:
        - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
          performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5.
          ``"paper_pseudocode"`` follows the pseudocode in the paper's Appendix B, and the test suite compares `ITP`
          with the iteration counts in the paper's Table 1. https://doi.org/10.1145/3423597
        - The authors' MATLAB code that produced the paper's experiments, which ``"paper_experiments"`` follows. The
          authors shared it on request; it is not published.
    """

    name = "itp"
    version = 1
    state_cls = ITPState

    def __init__(self, *, n_slack: int, variant: ITPVariant) -> None:
        """Configure the method.

        Args:
            n_slack: The paper's ``n_0``, the number of iterations that the solve may take beyond the iteration count
                of bisection.
            variant: The paper's source for the projection radius ``r``: ``"paper_pseudocode"`` uses ``r`` as the
                pseudocode states it, and ``"paper_experiments"`` lowers ``r`` by the margin of the authors' MATLAB
                code. A plain string such as ``"paper_experiments"`` works too.

        Raises:
            ValueError: If ``n_slack`` is negative, or ``variant`` is not a value of `ITPVariant`.
        """
        if n_slack < 0:
            raise ValueError(f"n_slack must be at least 0 (got {n_slack}).")
        self.n_slack = n_slack
        self.variant = ITPVariant(variant)

    def _solve(self, state: ITPState) -> float:
        """Set the solve's ``kappa_1`` and first ``max_next_width`` on ``state``, then run `BracketingSolver`'s loop.

        The paper computes ``xtol * 2^(n_max - k)`` in every iteration; `ITP` computes it once and halves it every
        iteration, which gives the same values exactly.
        """
        width = state.interval.width
        n_bisection = math.ceil(math.log2(width / (2.0 * state.xtol)))
        state.kappa_1 = _KAPPA_1_TIMES_INITIAL_WIDTH / width
        state.max_next_width = state.xtol * 2.0 ** (n_bisection + self.n_slack)
        return super()._solve(state)

    def _next_x(self, state: ITPState, interval: Interval) -> float:
        """Return ``x_itp``, the interpolation point ``x_f`` truncated and projected as the class docstring says.

        Also halve ``state.max_next_width`` for the next iteration, so 2 calls on the same interval return different
        points.
        """
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
        delta = state.kappa_1 * interval.width**_KAPPA_2
        if delta <= abs(x_half_minus_x_f):
            x_t = x_f + sigma * delta
        else:
            x_t = x_half

        # --- projection -------------------------
        r = state.max_next_width - 0.5 * interval.width
        state.max_next_width = 0.5 * state.max_next_width
        if self.variant is ITPVariant.PAPER_EXPERIMENTS:
            # Apply the margin of the authors' MATLAB code; the class docstring describes its 2 effects.
            r = max(0.99 * r - 0.5 * state.xtol, 0.0)
        if abs(x_t - x_half) <= r:
            return x_t
        else:
            return x_half - sigma * r
