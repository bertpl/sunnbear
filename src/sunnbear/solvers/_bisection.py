"""`Bisection` is the reference bracketing solver."""

from ._interval import Interval
from ._run import SolveRun
from ._solver import BracketingSolver


class Bisection(BracketingSolver[None]):
    """`Bisection` halves the bracket at its midpoint every iteration.

    A solve from width ``w`` to tolerance ``xtol`` takes exactly
    ``ceil(log2(w / (2 * xtol)))`` iterations and two more evaluations than
    iterations.
    """

    name = "bisection"
    version = 1

    def _step(self, run: SolveRun, interval: Interval, state: None) -> tuple[Interval, None]:
        """Evaluate at the midpoint and keep the half that holds the sign change."""
        x = interval.midpoint
        return interval.replace(x, run.f(x)), None
