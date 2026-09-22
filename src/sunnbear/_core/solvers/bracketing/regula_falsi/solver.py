"""`RegulaFalsi` implements regula falsi, the bracketing algorithm based on linear interpolation."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, SolveState


class RegulaFalsi(BracketingSolver):
    """`RegulaFalsi` evaluates, every step, where the chord through the interval's bound points crosses zero.

    `RegulaFalsi` implements the classic method, without any of the modifications that repair its
    known weakness: when the function is convex or concave on the interval, 1 interval bound is
    retained forever and the width never shrinks below the distance from that bound to the root, so
    the stopping criterion never holds.

    Such a solve runs until its evaluation budget is exhausted and ends as ``MAX_FEVALS``, with the
    last iterate, which does converge to the root, as its ``result.x``.
    """

    name = "regula_falsi"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Return where the chord through the bound points crosses zero."""
        return (interval.a * interval.fb - interval.b * interval.fa) / (interval.fb - interval.fa)
