"""`MCTuplesRefinementSolve` moves each new tuple of a size within its fine cell, in the size's second max-div solve.

The selection solve (`selection`) picks each new tuple among the few candidates that its population draws in a fine
cell. The refinement solve draws a population only in the fine cells that the selection picked: each picked tuple,
followed by many candidates inside its fine cell (`MCTuplesPopulation.in_fine_cells_of`). Besides the constraint that
keeps the size below (`solve`), 1 constraint per picked fine cell holds exactly 1 new tuple in it.

A fine cell fixes a tuple's fine u-lane and fine v-lane, so every selection that meets these constraints keeps the
selection's gap counts and its limit of 1 tuple per fine lane. max-div starts from the selection's tuples, so the
refinement ends with a score at least as high as theirs.
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
    """`MCTuplesRefinementSolve` is the max-div solve that moves the new tuples of 1 size within their fine cells.

    Attributes:
        n_candidates_per_cell: The number of candidates that the population draws in each fine cell, besides the
            selected tuple.
    """

    def __init__(
        self,
        n_candidates_per_cell: int,
        required_tuple_array: np.ndarray,
        selected_new_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: MCTuplesSolveSettings,
    ) -> None:
        """Draw the population in the fine cells of `selected_new_tuple_array`, the selection solve's new tuples.

        Drawing the population advances `settings.rng`.
        """
        self.n_candidates_per_cell = n_candidates_per_cell
        population = MCTuplesPopulation.in_fine_cells_of(selected_new_tuple_array, n_candidates_per_cell, settings.rng)
        super().__init__(population, required_tuple_array, size, settings)

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _new_tuple_constraints(self) -> list[Constraint]:
        """Return 1 constraint per fine cell, which holds exactly 1 new tuple in it."""
        n_required = self.size.n_required
        n_per_cell = self.n_candidates_per_cell + 1
        return [
            Constraint(int_set=set(range(start, start + n_per_cell)), min_count=1, max_count=1)
            for start in n_required + n_per_cell * np.arange(self.size.n_new)
        ]

    def _initial_new_selection(self) -> np.ndarray:
        """Return the selection's new tuples, the first candidate of each fine cell, as indices into the population."""
        return (self.n_candidates_per_cell + 1) * np.arange(self.size.n_new)

    def _check_new_selection(self, new: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if a fine cell holds no new tuple, or 2 or more."""
        counts = np.bincount(new // (self.n_candidates_per_cell + 1), minlength=self.size.n_new)
        n_off = int((counts != 1).sum())
        if n_off > 0:
            raise MCTuplesConstructionError(f"Size {self.size}: {n_off} fine cells do not hold exactly 1 new tuple.")
