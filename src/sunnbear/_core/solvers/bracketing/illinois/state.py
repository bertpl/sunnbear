"""This module declares `IllinoisState`, the state that `Illinois` carries between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import IntervalBound, SolveState


@dataclass
class IllinoisState(SolveState):
    """`IllinoisState` adds the Illinois method's 2 values that carry over from one iteration to the next.

    Attributes:
        newest_bound: The bound that holds the most recent iterate. Before the first iterate, the upper bound is the
            newest bound, as in the published method.
        scaled_retained_f: The function value that the chord uses at the retained bound, which is the bound that does
            not hold the most recent iterate. It equals that bound's own function value, halved once for every
            iteration that kept the bound again.
    """

    newest_bound: IntervalBound = field(init=False)
    scaled_retained_f: float = field(init=False)

    def __post_init__(self) -> None:
        """Start with the upper bound as the newest bound: `scaled_retained_f` is ``fa``."""
        self.newest_bound = IntervalBound.UPPER
        self.scaled_retained_f = self.interval.fa
