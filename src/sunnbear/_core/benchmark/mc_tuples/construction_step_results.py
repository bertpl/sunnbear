"""A step result records what 1 max-div step of the tuple-set construction produced and how its solve went.

`MCTuplesStepResult` holds what every step reports, and a subclass per step adds what the next step or the caller
needs:

- `MCTuplesCellSelectionResult`: the selected cells;
- `MCTuplesRefinementResult`: the size's tuples as `MCTuples`.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

import numpy as np
from max_div.solver import ParallelMaxDivSolution

from .sizes import MCTuplesSize
from .tuples import MCTuples


# ==================================================================================================
#  MCTuplesStepKind
# ==================================================================================================
class MCTuplesStepKind(StrEnum):
    """`MCTuplesStepKind` names 1 of the 2 max-div steps that add the new tuples of a size."""

    CELL_SELECTION = "cell_selection"
    REFINEMENT = "refinement"


# ==================================================================================================
#  MCTuplesStepResult and its subclasses
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesStepResult:
    """`MCTuplesStepResult` describes 1 finished max-div step of a construction, for progress reports and inspection.

    Attributes:
        kind: The kind of step, the same for every result of a subclass.
        size: The size of the tuple set under construction.
        t_budget_sec: The solve's wall-clock budget.
        t_wall_sec: The step's wall-clock time: the budget, plus max-div's start-up and shut-down time and the time
            of the step's validation.
        tuple_array: The size's tuples after the step, the tuples of the size below first, as a `(size, 2)` array
            of (u, v) values:

            - after cell selection, the tuple that represents each selected cell (its new u value and new v value),
              which can lie on the edges of the unit square;
            - after refinement, the size's final tuples.
        solution: max-div's solution of the solve, with its score checkpoints and timeline.
    """

    kind: ClassVar[MCTuplesStepKind]

    size: MCTuplesSize
    t_budget_sec: float
    t_wall_sec: float
    tuple_array: np.ndarray
    solution: ParallelMaxDivSolution


@dataclass(frozen=True, kw_only=True)
class MCTuplesCellSelectionResult(MCTuplesStepResult):
    """`MCTuplesCellSelectionResult` is the result of cell selection: the cells where refinement places the new tuples.

    Attributes:
        cells: The selected cells of the size's lane grid, as ascending cell indices, 1 per new lane along each axis.
    """

    kind = MCTuplesStepKind.CELL_SELECTION

    cells: np.ndarray


@dataclass(frozen=True, kw_only=True)
class MCTuplesRefinementResult(MCTuplesStepResult):
    """`MCTuplesRefinementResult` is the result of refinement: the size's tuples, with 1 new tuple inside each selected cell.

    Attributes:
        tuples: The size's tuples, the tuples of the size below first, as the `MCTuples` that the construction
            extends at the next size; `tuple_array` holds the same values.
    """

    kind = MCTuplesStepKind.REFINEMENT

    tuples: MCTuples
