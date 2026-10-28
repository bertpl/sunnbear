"""`MCTuplesRefinementSolve` moves each new base tuple of a size within its fine cell, in the size's second solve.

The selection solve (`selection`) draws only a few candidates per fine cell, and picks each new base tuple among them.

The refinement solve draws a population only in the fine cells of the selected new base tuples: each base tuple,
followed by many candidates inside its fine cell (`MCTuplesPopulation.draw_in_fine_cells_of`).

Besides the weighted constraint that keeps the placeholder and the size below (`solve`), 1 constraint per fine cell of
a new base tuple requires exactly 1 new base tuple in that cell. A fine cell fixes a base tuple's 2 lower fine lanes, so
every set of new base tuples that meets these constraints keeps the limit of 1 tuple per fine lane.

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
    """`MCTuplesRefinementSolve` is the max-div solve that moves the new base tuples of 1 size within their fine cells.

    Attributes:
        n_random_candidates_per_cell: The number of candidates that the population draws in each fine cell, besides the
            selected base tuple.
    """

    def __init__(
        self,
        n_random_candidates_per_cell: int,
        selected_base_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: MCTuplesSolveSettings,
    ) -> None:
        """Draw the population in the fine cells of the new base tuples in `selected_base_tuple_array`.

        `selected_base_tuple_array` holds the size's base tuples after the selection solve: the size below's base
        tuples first, then the new base tuples. Drawing the population advances `settings.rng`.
        """
        self.n_random_candidates_per_cell = n_random_candidates_per_cell
        n_required_base_tuples = size.n_required // 4
        population = MCTuplesPopulation.draw_in_fine_cells_of(
            selected_base_tuple_array[n_required_base_tuples:], n_random_candidates_per_cell, settings.rng
        )
        super().__init__(population, selected_base_tuple_array[:n_required_base_tuples], size, settings)

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _new_tuple_constraints(self) -> list[Constraint]:
        """Return 1 constraint per fine cell of a new base tuple, each requiring exactly 1 new base tuple in it."""
        n_per_cell = self.n_random_candidates_per_cell + 1
        return [
            Constraint(int_set=set(range(start, start + n_per_cell)), min_count=1, max_count=1)
            for start in self.n_kept_candidates + n_per_cell * np.arange(self.n_new_base_tuples)
        ]

    def _initial_new_selection(self) -> np.ndarray:
        """Return the selected new base tuples, each fine cell's first candidate, as indices into the population."""
        return (self.n_random_candidates_per_cell + 1) * np.arange(self.n_new_base_tuples)

    def _check_new_selection(self, new_selection: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if a fine cell holds no new base tuple, or 2 or more."""
        counts = np.bincount(new_selection // (self.n_random_candidates_per_cell + 1), minlength=self.n_new_base_tuples)
        n_off = int((counts != 1).sum())
        if n_off > 0:
            raise MCTuplesConstructionError(
                f"Size {self.size}: {n_off} fine cells do not hold exactly 1 new base tuple."
            )
