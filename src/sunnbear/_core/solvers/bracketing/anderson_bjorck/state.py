"""This module declares `AndersonBjorckState`, the state that `AndersonBjorck` carries between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import IntervalBound, SolveState


@dataclass
class AndersonBjorckState(SolveState):
    """`AndersonBjorckState` adds the Anderson-Björck method's values that carry over from one iteration to the next.

    The ALGOL procedure of Anderson and Björck (1973) names the most recent iterate ``x1``, its function value ``f1``,
    the retained bound ``x0``, and the retained bound's scaled function value ``f0``.

    Attributes:
        newest_bound: The bound that holds the most recent iterate ``x1``. Before the first iterate, it is the upper
            bound, for the reason that the "Starting order" bullet of the `AndersonBjorck` class docstring gives.
        newest_x: The most recent iterate ``x1``. The factor needs it after the next iterate has replaced the newest
            bound, because the interval then no longer holds ``x1``.
        newest_f: The function value ``f1`` at the most recent iterate, kept for the same reason.
        scaled_retained_f: The function value ``f0`` that the chord uses at the retained bound ``x0``, which is the
            bound that does not hold the most recent iterate. It equals that bound's own function value, multiplied by
            the factor of every iteration that kept the bound again.
    """

    newest_bound: IntervalBound = field(init=False)
    newest_x: float = field(init=False)
    newest_f: float = field(init=False)
    scaled_retained_f: float = field(init=False)

    def __post_init__(self) -> None:
        """Start with the upper bound ``b`` as the newest bound, and ``fa`` as `scaled_retained_f`."""
        self.newest_bound = IntervalBound.UPPER
        self.newest_x = self.interval.b
        self.newest_f = self.interval.fb
        self.scaled_retained_f = self.interval.fa
