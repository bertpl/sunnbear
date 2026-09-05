"""`RegulaFalsi` is the reference solver for the ``MAX_FEVALS`` outcome: its plain form stalls on curved functions."""

from ._interval import Interval
from ._run import SolveRun
from ._solver import BracketingSolver


class RegulaFalsi(BracketingSolver[None]):
    """`RegulaFalsi` splits the bracket at the secant point of its endpoints every iteration.

    The solver is included as the reference case for the ``MAX_FEVALS``
    outcome, not as a competitive method. In this plain form one endpoint is
    retained forever on a convex or concave function, so the bracket width
    never falls below the distance from that endpoint to the root; the solve
    then ends either through an exact zero at the moving endpoint or by
    running into its evaluation budget.
    """

    name = "regula_falsi"
    version = 1

    def _step(self, run: SolveRun, interval: Interval, state: None) -> tuple[Interval, None]:
        """Evaluate at the secant point and keep the half that holds the sign change."""
        x = interval.b - interval.fb * interval.width / (interval.fb - interval.fa)
        return interval.replace(x, run.f(x)), None
