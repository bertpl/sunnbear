"""`MCTuplesSizeResult` records how 1 size of the tuple-set construction was built: its 2 solves."""

from dataclasses import dataclass

import numpy as np
from max_div.solver import ParallelMaxDivSolution

from sunnbear._core.benchmark.mc_tuples.core import MCTuples, MCTuplesSize

from .rotations import tuple_array_of


# ==================================================================================================
#  MCTuplesSizeResult
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesSizeResult:
    """`MCTuplesSizeResult` describes 1 finished size of a construction, for progress reports and inspection.

    The base tuple arrays are `(size / 4, 2)` arrays: the size below's base tuples first, then the new base tuples.

    Attributes:
        size: The size built, in tuples.
        t_budget_sec: The wall-clock budget of the size's 2 max-div solves together.
        t_wall_sec: The size's wall-clock time: its 2 populations and its 2 solves, with max-div's start-up and
            shut-down time.
        selected_base_tuple_array: The size's base tuples after the selection solve.
        refined_base_tuple_array: The size's base tuples after the refinement solve, the final ones.
        selection_solution: max-div's solution of the selection solve, with its score checkpoints and timeline.
        refinement_solution: max-div's solution of the refinement solve, with its score checkpoints and timeline.
    """

    size: MCTuplesSize
    t_budget_sec: float
    t_wall_sec: float
    selected_base_tuple_array: np.ndarray
    refined_base_tuple_array: np.ndarray
    selection_solution: ParallelMaxDivSolution
    refinement_solution: ParallelMaxDivSolution

    @property
    def selected_tuple_array(self) -> np.ndarray:
        """Return the size's tuples after the selection solve, with the size below's tuples first."""
        return tuple_array_of(self.selected_base_tuple_array)

    @property
    def tuples(self) -> MCTuples:
        """Return the size's final tuples, with the size below's tuples first."""
        tuple_array = tuple_array_of(self.refined_base_tuple_array)
        return MCTuples(tuple_array[:, 0], tuple_array[:, 1])
