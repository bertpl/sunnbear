"""`MCTuplesSizeResult` records how 1 size of the tuple-set construction was built: allocation, solve, correction."""

from dataclasses import dataclass

import numpy as np
from max_div.solver import ParallelMaxDivSolution

from sunnbear._core.benchmark.mc_tuples.core import MCTuples, MCTuplesSize

from .allocation import GapAllocation
from .correction import MeanCorrection


# ==================================================================================================
#  MCTuplesSizeResult
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesSizeResult:
    """`MCTuplesSizeResult` describes 1 finished size of a construction, for progress reports and inspection.

    Attributes:
        size: The size built.
        t_budget_sec: The max-div solve's wall-clock budget.
        t_wall_sec: The size's wall-clock time: the population, the gap allocation, the solve with max-div's start-up
            and shut-down time, and the mean correction.
        gap_allocation: The allocation of the new tuples to the gaps along u and along v.
        uncorrected_tuple_array: The size's tuples before the mean correction, as a `(size, 2)` array of (u, v)
            values: the size below's tuples first, then the new tuples that max-div selected.
        mean_correction: The mean correction, with what it did on each axis and the size's tuples after it.
        solution: max-div's solution of the solve, with its score checkpoints and timeline.
    """

    size: MCTuplesSize
    t_budget_sec: float
    t_wall_sec: float
    gap_allocation: GapAllocation
    uncorrected_tuple_array: np.ndarray
    mean_correction: MeanCorrection
    solution: ParallelMaxDivSolution

    @property
    def tuples(self) -> MCTuples:
        """Return the size's tuples after the mean correction, with the size below's tuples first."""
        tuple_array = self.mean_correction.tuple_array
        return MCTuples(tuple_array[:, 0], tuple_array[:, 1])
