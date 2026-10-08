"""`MCTuplesSizeResult` records how 1 size of the tuple-set construction was built: its allocation, solve and correction."""

from dataclasses import dataclass

import numpy as np
from max_div.solver import ParallelMaxDivSolution

from .construction_correction import MeanCorrection
from .construction_gaps import GapAllocation
from .sizes import MCTuplesSize
from .tuples import MCTuples


# ==================================================================================================
#  MCTuplesSizeResult
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesSizeResult:
    """`MCTuplesSizeResult` describes 1 finished size of a construction, for progress reports and inspection.

    Attributes:
        size: The size built.
        t_budget_sec: The max-div solve's wall-clock budget.
        t_wall_sec: The size's wall-clock time: the population, the solve with max-div's start-up and shut-down time,
            and the mean correction.
        u_allocation: The allocation of the new tuples to the gaps along u.
        v_allocation: The allocation of the new tuples to the gaps along v.
        uncorrected_tuple_array: The size's tuples as max-div selected them, before the mean correction, the size
            below's first, as a `(size, 2)` array of (u, v) values.
        correction: The mean correction, with what it did on each axis.
        tuples: The size's tuples after the mean correction, the size below's first, as the `MCTuples` that the
            construction extends at the next size.
        solution: max-div's solution of the solve, with its score checkpoints and timeline.
    """

    size: MCTuplesSize
    t_budget_sec: float
    t_wall_sec: float
    u_allocation: GapAllocation
    v_allocation: GapAllocation
    uncorrected_tuple_array: np.ndarray
    correction: MeanCorrection
    tuples: MCTuples
    solution: ParallelMaxDivSolution
