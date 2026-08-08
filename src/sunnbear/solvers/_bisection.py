"""Bisection: the reference bracketing solver.

Beyond its role as a baseline, bisection anchors the benchmarking
methodology: the x-tolerance range of a benchmark is derived from the number
of iterations bisection needs, and early bisection convergence is the
degeneracy probe for candidate test functions. Its exact iteration behavior
(``n_fevals = n_iters + 2``; halving until ``width <= 2 * xtol``) is therefore
a framework invariant, pinned by tests.
"""

from ._interval import Interval
from ._run import SolveRun
from ._solver import BracketingSolver, StepOutcome


# ==================================================================================================
#  Bisection
# ==================================================================================================
class Bisection(BracketingSolver[None]):
    """Halve the bracket at its midpoint each iteration."""

    name = "bisection"
    version = 1

    def _step(self, run: SolveRun, interval: Interval, state: None) -> StepOutcome[None]:
        """Evaluate the midpoint and keep the sign-changing half."""
        x = interval.midpoint
        return StepOutcome(interval=interval.replace(x, run.f(x)), state=None)
