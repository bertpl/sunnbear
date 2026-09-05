"""`RegulaFalsi` is the second reference bracketing solver, and the one that exercises the failure path."""

from ._interval import Interval
from ._run import SolveRun
from ._solver import BracketingSolver


class RegulaFalsi(BracketingSolver[None]):
    """`RegulaFalsi` splits the bracket at the secant point of its endpoints every iteration.

    In this plain form one endpoint is retained forever on a convex or concave
    function, so the bracket width never falls below the distance from that
    endpoint to the root. The solve then ends either through an exact zero at
    the moving endpoint or by running into its evaluation budget. That is
    deliberate: the solver is included as the reference case for the
    ``MAX_FEVALS`` path, not as a competitive method.
    """

    name = "regula_falsi"
    version = 1

    def _step(self, run: SolveRun, interval: Interval, state: None) -> tuple[Interval, None]:
        """Evaluate at the secant point and keep the half that holds the sign change."""
        x = interval.b - interval.fb * interval.width / (interval.fb - interval.fa)
        return interval.replace(x, run.f(x)), None
