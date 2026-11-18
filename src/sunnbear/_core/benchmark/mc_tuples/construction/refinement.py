"""`MCTuplesRefinementSolve`, a size's second solve, moves each new base tuple within its LHS cell of the largest size.

The selection solve (`selection`) draws only a few candidates per LHS cell of the largest size, so each new base tuple
that it picks can still move to a better position within that cell.

The refinement solve draws a population only in the selected new base tuples' LHS cells of the largest size: each base
tuple, followed by many candidates inside its cell (`MCTuplesPopulation.draw_in_lhs_cells_of`).

Besides the weighted constraint that keeps the dummy rotational sibling tuple and the size below (`solve`), 1 constraint
per new base tuple's LHS cell of the largest size requires exactly 1 new base tuple in that cell.

Every size's LHS lanes are made of whole LHS lanes of the largest size, and its tiles of whole LHS cells of the largest
size, so a base tuple that moves within its LHS cell of the largest size keeps its LHS lanes and its tile at every size.

max-div starts from the selected base tuples, so the refinement ends with a score at least as high as theirs.
"""

import numpy as np
from max_div import Constraint

from sunnbear._core.benchmark.mc_tuples.core import MCTuplesSize

from .exceptions import MCTuplesConstructionError
from .population import MCTuplesPopulation
from .solve import MCTuplesSolve, MCTuplesSolveSettings


# ==================================================================================================
#  MCTuplesRefinementSolve
# ==================================================================================================
class MCTuplesRefinementSolve(MCTuplesSolve):
    """`MCTuplesRefinementSolve` is the max-div solve that moves a size's new base tuples within their LHS cells.

    Their LHS cells are those of the largest size.

    Attributes:
        n_random_candidates_per_cell: The number of candidates that the population draws in each LHS cell of the largest
            size of a new base tuple, besides the selected base tuple.
    """

    def __init__(
        self,
        n_random_candidates_per_cell: int,
        selected_base_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: MCTuplesSolveSettings,
    ) -> None:
        """Draw the population in the new base tuples' LHS cells of the largest size.

        `selected_base_tuple_array` holds the size's base tuples after the selection solve: the size below's base
        tuples first, then the new base tuples. Drawing the population advances `settings.rng`.
        """
        self.n_random_candidates_per_cell = n_random_candidates_per_cell
        n_required_base_tuples = size.n_required // 4
        population = MCTuplesPopulation.draw_in_lhs_cells_of(
            selected_base_tuple_array[n_required_base_tuples:],
            n_random_candidates_per_cell,
            max(MCTuplesSize),
            settings.rng,
        )
        super().__init__(population, selected_base_tuple_array[:n_required_base_tuples], size, settings)

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _new_base_tuple_constraints(self) -> list[Constraint]:
        """Return 1 constraint per new base tuple's LHS cell of the largest size.

        Each constraint requires exactly 1 new base tuple in its cell.
        """
        n_per_cell = self.n_random_candidates_per_cell + 1
        return [
            Constraint(int_set=set(range(start, start + n_per_cell)), min_count=1, max_count=1)
            for start in self.n_always_selected_candidates + n_per_cell * np.arange(self.n_new_base_tuples)
        ]

    def _initial_new_selection(self) -> np.ndarray:
        """Return the selected new base tuples as indices into the population.

        They are the first candidate of each LHS cell of the largest size.
        """
        return (self.n_random_candidates_per_cell + 1) * np.arange(self.n_new_base_tuples)

    def _check_new_selection(self, new_selection: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` unless each LHS cell of the largest size holds exactly 1 new base tuple."""
        counts = np.bincount(new_selection // (self.n_random_candidates_per_cell + 1), minlength=self.n_new_base_tuples)
        n_off = int((counts != 1).sum())
        if n_off > 0:
            raise MCTuplesConstructionError(
                f"Size {self.size}: {n_off} LHS cells of the largest size do not hold exactly 1 new base tuple."
            )
