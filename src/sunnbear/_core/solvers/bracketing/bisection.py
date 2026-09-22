"""`Bisection` is the reference bracketing solver."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, SolveState


class Bisection(BracketingSolver):
    """`Bisection` splits the interval at its midpoint every step, so each step halves the width.

    The evaluation count is exact and known in advance: with the interval width ``b - a`` and the
    tolerance ``xtol``, a solve performs ``ceil(log2((b - a) / (2 * xtol)))`` steps, 1 evaluation
    each, plus the 2 evaluations at the interval bounds.

    The solve performs fewer evaluations only when a midpoint is an exact root.

    The benchmark relies on that exact count as its reference cost, so it must not change.
    """

    name = "bisection"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Return the midpoint."""
        return interval.midpoint
