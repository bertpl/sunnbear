"""This module declares `FordState`, `Ford`'s state between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import IntervalBound, SolveState


@dataclass
class FordState(SolveState):
    """`FordState` adds the values of Ford's methods that carry over from one iteration to the next.

    Ford (1997) names the most recent iterate ``x_i``, or ``s`` in the step formula, and the retained bound ``x_(i-1)``,
    or ``r``.

    Attributes:
        newest_bound: The bound that holds the most recent iterate ``x_i``. Before the first iterate, it is the upper
            bound; the "Starting order" bullet of the `Ford` class docstring gives the reason.
        newest_x: The most recent iterate ``x_i``. The factor ``gamma`` needs it after the next iterate has replaced
            the newest bound, because the interval then no longer holds ``x_i``.
        newest_f: The function value ``f_i`` at the most recent iterate, kept for the same reason.
        scaled_retained_f: The secant's function value at the retained bound ``x_(i-1)``, which is the bound that
            does not hold the most recent iterate. It equals that bound's own function value, multiplied by the
            ``gamma`` of every iteration that kept the bound again.
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
