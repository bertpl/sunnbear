"""Regula falsi (false position): secant-point bracketing without endpoint aging.

The classic textbook form: each step evaluates the secant intersection of the
current bracket's endpoints and keeps the sign-changing half. On functions
with pronounced curvature one endpoint is retained indefinitely, so the
bracket width never contracts to the tolerance — the run then terminates via
the function-evaluation budget. That stall is intrinsic to the method (the
Illinois and Pegasus variants exist to repair it) and makes this solver a
useful reference for exercising budget-capped terminations.
"""

from ._interval import Interval
from ._run import SolveRun
from ._solver import BracketingSolver, StepOutcome


# ==================================================================================================
#  RegulaFalsi
# ==================================================================================================
class RegulaFalsi(BracketingSolver[None]):
    """Reduce the bracket at the secant point of its endpoints each iteration."""

    name = "regula_falsi"
    version = 1

    def _step(self, run: SolveRun, interval: Interval, state: None) -> StepOutcome[None]:
        """Evaluate the secant intersection and keep the sign-changing half."""
        a, b, fa, fb = interval.a, interval.b, interval.fa, interval.fb
        x = b - fb * (b - a) / (fb - fa)
        return StepOutcome(interval=interval.replace(x, run.f(x)), state=None)
