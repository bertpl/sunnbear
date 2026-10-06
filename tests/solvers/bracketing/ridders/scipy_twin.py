"""`RiddersScipyTwin` runs `scipy.optimize.ridder` as a `Solver`, so `Ridders` can be tested against it."""

from typing import Literal

import numpy as np
import scipy.optimize

from sunnbear.solvers import Interval
from tests.solvers.twins import TwinFunction, TwinSolver


class RiddersScipyTwin(TwinSolver):
    """`RiddersScipyTwin` hands the interval to `scipy.optimize.ridder` and returns the root estimate at the point
    where `Ridders`, with the same stopping criterion, would stop.

    SciPy stops once its interval is narrower than its tolerance, which matches neither of the 2 stopping criteria of
    `Ridders`. The twin passes SciPy its smallest accepted tolerance, so that SciPy does not stop first, and stops it
    with the criterion of `Ridders` through `_root_if_sunnbear_solver_stops`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first midpoint;
    - SciPy computes each midpoint as a bound plus a halved step, and does not keep its 2 bounds in order, so it
      computes an iterate from whichever bound it holds as the first; before SciPy 1.18, it also computed the iterate
      with an equivalent formula of its own. SciPy's midpoints and iterates can therefore differ from those of
      `Ridders` in their last bits;
    - SciPy keeps each iterate at least half its tolerance away from the interval bounds; at the smallest tolerance,
      this moves an iterate by a few ulps at most.
    """

    name = "ridders_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def __init__(self, *, stopping_criterion: Literal["original", "corrected"]) -> None:
        """Take the stopping criterion of the twin's `Ridders` config."""
        self.stopping_criterion = stopping_criterion

    def _run_reference(self, f: TwinFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's ridder with its smallest accepted tolerance."""
        finfo = np.finfo(float)
        scipy.optimize.ridder(f, a, b, xtol=float(finfo.smallest_normal), rtol=4.0 * float(finfo.eps))

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return the root estimate if `Ridders` stops here: at a zero, or after an iteration that meets its criterion.

        The evaluations alternate between a midpoint and an iterate, so an odd count ends with a midpoint, after
        which `Ridders` stops only at a zero.
        """
        x, fx = evaluations[-1]
        if fx == 0.0:
            return x
        elif len(evaluations) % 2 == 1:
            return None
        elif self.stopping_criterion == "original":
            # The previous iterate lies 2 evaluations back, before the midpoint of this iteration.
            if len(evaluations) >= 4 and abs(x - evaluations[-3][0]) <= xtol:
                return x
            else:
                return None
        else:
            return super()._root_if_sunnbear_solver_stops(interval, evaluations, xtol)
