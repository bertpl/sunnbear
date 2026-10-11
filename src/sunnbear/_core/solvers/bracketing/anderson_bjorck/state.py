"""This module declares `AndersonBjorckState`, the state of `AndersonBjorck` between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import IntervalBound, SolveState


@dataclass
class AndersonBjorckState(SolveState):
    """`AndersonBjorckState` adds the Anderson-Björck method's values that carry over from one iteration to the next.

    Attributes:
        newest_bound: The bound that holds the most recent iterate. Before the first iterate, the upper bound is the
            newest bound, as in `Illinois` and in mpmath's implementation of both methods.
        newest_x: The most recent iterate. The factor's slope from the previous to the new iterate needs this value
            after the next iterate has replaced the newest bound, because the interval then no longer holds the
            previous iterate.
        newest_f: The function value at the newest bound, which that slope needs for the same reason.
        scaled_retained_f: The chord's function value at the retained bound, which is the bound that does not hold
            the most recent iterate. The scaled value equals the retained bound's own function value, multiplied by the
            scaling factor of every iteration that kept the bound again.
        chord_slope: The slope of the chord that produced the most recent iterate, which the factor divides by; each
            call of `AndersonBjorck._next_x` sets it.
    """

    newest_bound: IntervalBound = field(init=False)
    newest_x: float = field(init=False)
    newest_f: float = field(init=False)
    scaled_retained_f: float = field(init=False)
    chord_slope: float = field(init=False)

    def __post_init__(self) -> None:
        """Start with the upper bound as the newest bound, at ``b`` and ``fb``; `scaled_retained_f` is ``fa``."""
        self.newest_bound = IntervalBound.UPPER
        self.newest_x = self.interval.b
        self.newest_f = self.interval.fb
        self.scaled_retained_f = self.interval.fa
