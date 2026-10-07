"""This module declares `AndersonBjorckState`, the state of `AndersonBjorck` between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import IntervalBound, SolveState


@dataclass
class AndersonBjorckState(SolveState):
    """`AndersonBjorckState` adds the Anderson-Björck method's values that carry over from one iteration to the next.

    Attributes:
        newest_bound: The bound that holds the most recent iterate. Before the first iterate, the upper bound is the
            newest bound, as in `Illinois` and in mpmath's implementation of both methods.
        newest_f: The function value at the newest bound. `AndersonBjorck` scales the other bound's value by
            ``1 - f_new / f_previous``, and needs this value as ``f_previous`` after the next iterate has replaced the
            newest bound, because the interval then no longer holds the previous iterate.
        scaled_retained_f: The chord's function value at the retained bound, which is the bound that does not hold
            the most recent iterate. The scaled value equals the retained bound's own function value, multiplied by the
            scaling factor of every iteration that kept the bound again.
    """

    newest_bound: IntervalBound = IntervalBound.UPPER
    newest_f: float = field(init=False)
    scaled_retained_f: float = field(init=False)

    def __post_init__(self) -> None:
        """Set the starting values from the interval: `newest_f` is ``fb`` and `scaled_retained_f` is ``fa``.

        These values hold only for the default `newest_bound`.
        """
        self.newest_f = self.interval.fb
        self.scaled_retained_f = self.interval.fa
