"""`RegulaFalsi` is a reference bracketing solver: the example of a solve that stalls."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, SolveState


class RegulaFalsi(BracketingSolver):
    """`RegulaFalsi` evaluates, every step, where the chord through the interval's bound points crosses zero.

    The classic method, without any of the modifications that repair its known weakness: when the
    function is convex or concave on the interval, one interval bound is retained forever and the
    width never shrinks below the distance from that bound to the root, so the stopping criterion
    never holds.

    Such a solve runs until its evaluation budget is exhausted and ends as ``MAX_FEVALS``. Its
    ``result.x`` is then the midpoint between the converging iterate and the retained bound, not a
    good root estimate; the converging iterate is the last entry of ``result.history``. This solver
    is the reference example of that failure path.
    """

    name = "regula_falsi"
    version = 1

    def _step(self, state: SolveState, interval: Interval) -> Interval:
        """Evaluate the secant point of the bound points and keep the half that holds the sign change."""
        x = (interval.a * interval.fb - interval.b * interval.fa) / (interval.fb - interval.fa)
        return interval.split_at(x, state.f(x))
