"""`MCTuplesSizeResult` records how 1 size of the tuple-set construction was built: allocation, solves, corrections."""

from dataclasses import dataclass

import numpy as np
from max_div.solver import ParallelMaxDivSolution

from sunnbear._core.benchmark.mc_tuples.core import MCTuples, MCTuplesSize

from .allocation import MCTuplesGapAllocation
from .correction import MCTuplesMeanCorrection


# ==================================================================================================
#  MCTuplesSizeResult
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesSizeResult:
    """`MCTuplesSizeResult` describes 1 finished size of a construction, for progress reports and inspection.

    The tuple arrays are `(size, 2)` arrays of (u, v) values: the size below's tuples first, then the new tuples.

    Attributes:
        size: The size built.
        t_budget_sec: The wall-clock budget of the size's 2 max-div solves together.
        t_wall_sec: The size's wall-clock time, which covers:

            - the gap allocation;
            - the 2 populations;
            - the 2 solves, with max-div's start-up and shut-down time;
            - the 2 mean corrections.
        gap_allocation: The allocation of the new tuples to the gaps along u and along v.
        selected_tuple_array: The size's tuples after the selection solve.
        first_mean_correction: The mean correction after the selection solve, with what the correction did on each
            axis and the size's tuples after the correction; the refinement solve starts from those tuples.
        refined_tuple_array: The size's tuples after the refinement solve.
        second_mean_correction: The mean correction after the refinement solve, with the size's final tuples.
        selection_solution: max-div's solution of the selection solve, with its score checkpoints and timeline.
        refinement_solution: max-div's solution of the refinement solve, with its score checkpoints and timeline.
    """

    size: MCTuplesSize
    t_budget_sec: float
    t_wall_sec: float
    gap_allocation: MCTuplesGapAllocation
    selected_tuple_array: np.ndarray
    first_mean_correction: MCTuplesMeanCorrection
    refined_tuple_array: np.ndarray
    second_mean_correction: MCTuplesMeanCorrection
    selection_solution: ParallelMaxDivSolution
    refinement_solution: ParallelMaxDivSolution

    @property
    def tuples(self) -> MCTuples:
        """Return the size's tuples after the second mean correction, with the size below's tuples first."""
        tuple_array = self.second_mean_correction.tuple_array
        return MCTuples(tuple_array[:, 0], tuple_array[:, 1])
