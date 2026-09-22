"""`Bisection` is the reference bracketing solver: it halves the interval at its midpoint every step."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, SolveState


class Bisection(BracketingSolver):
    """`Bisection` splits the interval at its midpoint every step, so each step halves the width.

    The evaluation count is exact and known in advance: with the interval width ``b - a``, a solve
    performs ``ceil(log2((b - a) / (2 * xtol)))`` steps, 1 evaluation each, plus the 2 evaluations
    at the interval bounds. The solve performs fewer evaluations only when a midpoint is an exact root.

    The benchmark relies on that exact count as its reference cost, so it must not change.
    """

    name = "bisection"
    version = 1

    def _step(self, state: SolveState, interval: Interval) -> Interval:
        """Evaluate the midpoint and keep the half that holds the sign change."""
        x = interval.midpoint
        return interval.split_at(x, state.f(x))
