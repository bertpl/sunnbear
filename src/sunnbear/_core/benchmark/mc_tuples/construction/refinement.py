"""`MCTuplesRefinementSolve` moves each new tuple of a size within its fine cell, in the size's second max-div solve.

The selection solve (`selection`) picks each new tuple among the few candidates that its population draws in a fine
cell. The refinement solve draws a population only in the fine cells that the selection solve picked: each picked
tuple, followed by many candidates inside its fine cell (`MCTuplesPopulation.draw_in_fine_cells_of`).

Besides the constraint that keeps the size below (`solve`), 1 constraint per picked fine cell requires exactly 1 new
tuple in that cell.

A fine cell fixes a tuple's fine u-lane and fine v-lane, so every set of new tuples that meets these constraints keeps
the selection solve's number of new tuples per gap and its limit of 1 tuple per fine lane. max-div starts from the
selection solve's tuples, so the refinement ends with a score at least as high as theirs.
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
        unrefined_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: MCTuplesSolveSettings,
    ) -> None:
        """Draw the population in the fine cells of the new tuples in `unrefined_tuple_array`.

        `unrefined_tuple_array` holds the selection solve's tuples of the size: the size below's tuples first, then the
        new tuples. Drawing the population advances `settings.rng`.
        """
        self.n_candidates_per_cell = n_candidates_per_cell
        population = MCTuplesPopulation.draw_in_fine_cells_of(
            unrefined_tuple_array[size.n_required :], n_candidates_per_cell, settings.rng
        )
        super().__init__(population, unrefined_tuple_array[: size.n_required], size, settings)

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _new_tuple_constraints(self) -> list[Constraint]:
        """Return 1 constraint per fine cell of a new tuple, each requiring exactly 1 new tuple in that cell."""
        n_required = self.size.n_required
        n_per_cell = self.n_candidates_per_cell + 1
        return [
            Constraint(int_set=set(range(start, start + n_per_cell)), min_count=1, max_count=1)
            for start in n_required + n_per_cell * np.arange(self.size.n_new)
        ]

    def _initial_new_selection(self) -> np.ndarray:
        """Return the selection solve's tuples, each fine cell's first candidate, as indices into the population."""
        return (self.n_candidates_per_cell + 1) * np.arange(self.size.n_new)

    def _check_new_selection(self, new: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if a fine cell holds no new tuple, or 2 or more."""
        counts = np.bincount(new // (self.n_candidates_per_cell + 1), minlength=self.size.n_new)
        n_off = int((counts != 1).sum())
        if n_off > 0:
            raise MCTuplesConstructionError(f"Size {self.size}: {n_off} fine cells do not hold exactly 1 new tuple.")
