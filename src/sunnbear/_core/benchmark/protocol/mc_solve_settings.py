"""`MCSolveSettings` holds the settings of a test problem's solves at the tuples of a Monte Carlo tuple set."""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.problems.core import TestProblem

from .c_range import CRange
from .tolerances import compute_xtol_range, max_fevals_for


# ==================================================================================================
#  MCSolveSettings
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCSolveSettings:
    """`MCSolveSettings` holds the `xtol`, the ``c`` and the evaluation budget of a test problem's solve at each tuple.

    Each tuple ``(u, v)`` of `mc_tuples` sets the tolerance and the parameter of 1 solve:

    - ``u`` sets `xtol` log-uniformly within the range from `compute_xtol_range`;
    - ``v`` sets ``c`` linearly within `c_range`.

    Every solve has the same evaluation budget, `max_fevals`.

    Attributes:
        a: The lower bound of the test problem's interval.
        b: The upper bound of the test problem's interval.
        n_bisection_fevals: The number of evaluations that bisection spends on each solve, from which the `xtol` range
            and the evaluation budget follow.
        c_range: The range within which ``c`` is sampled.
        mc_tuples: The tuples, 1 per solve.
    """

    a: float
    b: float
    n_bisection_fevals: int
    c_range: CRange
    mc_tuples: MCTuples

    # --------------------------------------------------------------------------
    #  Settings per solve
    # --------------------------------------------------------------------------
    @property
    def xtols(self) -> np.ndarray:
        """Return the `xtol` of every tuple, ``xtol_min * (xtol_max / xtol_min)^u``, in tuple order.

        `xtol_min` and `xtol_max` are the bounds of the range from `compute_xtol_range`.
        """
        xtol_min, xtol_max = compute_xtol_range(a=self.a, b=self.b, n_bisection_fevals=self.n_bisection_fevals)
        return xtol_min * np.exp2(self.mc_tuples.u * np.log2(xtol_max / xtol_min))

    @property
    def cs(self) -> np.ndarray:
        """Return the ``c`` of every tuple, in tuple order."""
        return self.map_v_onto_c_range(self.mc_tuples.v, self.c_range)

    @property
    def max_fevals(self) -> int:
        """Return the evaluation budget of every solve, from `max_fevals_for`."""
        return max_fevals_for(n_bisection_fevals=self.n_bisection_fevals)

    @staticmethod
    def map_v_onto_c_range(v: np.ndarray, c_range: CRange) -> np.ndarray:
        """Return ``c = c_min + v * (c_max - c_min)`` for each value of `v`, so that ``c`` is uniform within `c_range`.

        Calibration calls this method to find the c-values that the benchmark samples within a trial c-range.
        """
        return c_range.c_min + v * (c_range.c_max - c_range.c_min)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_test_problem(
        cls, problem: TestProblem, *, n_bisection_fevals: int, mc_tuples: MCTuples
    ) -> "MCSolveSettings":
        """Return the settings of the solves of a calibrated test problem, with its interval and its c-range."""
        return cls(
            a=problem.a,
            b=problem.b,
            n_bisection_fevals=n_bisection_fevals,
            c_range=CRange(c_min=problem.c_min, c_max=problem.c_max),
            mc_tuples=mc_tuples,
        )
