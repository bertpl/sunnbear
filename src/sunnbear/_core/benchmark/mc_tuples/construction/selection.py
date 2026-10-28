"""`MCTuplesSelectionSolve` picks a size's new base tuples from its population in the size's first max-div solve.

The population lies in the off-diagonal fine cells of the free lower fine lanes, those of [0, 0.5] that the size below's
base tuples leave free (`MCTuplesPopulation.draw_in_off_diagonal_cells`).

Besides the weighted constraint that keeps the placeholder and the size below (`solve`), 1 constraint per free lower
fine lane allows at most 1 new base tuple whose u or v lies in that lane.

At the largest size, the new base tuples need every free lower fine lane, so the number of selected candidates,
max-div's `k`, forces each lane to be used.

max-div starts from a random selection that meets these constraints (`_initial_new_selection`).
"""

import numpy as np
from max_div import Constraint

from sunnbear._core.benchmark.mc_tuples.core import MCTuplesSize, fine_lanes_of
from sunnbear._core.utils.grouping import group_indices_by_id

from .exceptions import MCTuplesConstructionError
from .population import MCTuplesPopulation
from .rotations import N_LOWER_FINE_LANES
from .solve import MCTuplesSolve, MCTuplesSolveSettings


# ==================================================================================================
#  MCTuplesSelectionSolve
# ==================================================================================================
class MCTuplesSelectionSolve(MCTuplesSolve):
    """`MCTuplesSelectionSolve` is the max-div solve that picks the new base tuples of 1 size from its population.

    Attributes:
        free_lanes: The lower fine lanes that hold no value of the size below's base tuples, ascending.
    """

    def __init__(
        self,
        n_population: int,
        required_base_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: MCTuplesSolveSettings,
    ) -> None:
        """Draw the size's population of about `n_population` candidates over the free lower fine lanes.

        Drawing the population advances `settings.rng`.
        """
        occupied_lanes = fine_lanes_of(required_base_tuple_array.ravel())
        self.free_lanes = np.setdiff1d(np.arange(N_LOWER_FINE_LANES), occupied_lanes)
        population = MCTuplesPopulation.draw_in_off_diagonal_cells(n_population, self.free_lanes, settings.rng)
        super().__init__(population, required_base_tuple_array, size, settings)

    @staticmethod
    def work_of(n_population: int, size: MCTuplesSize) -> int:
        """Return the solve's number of candidates times its number of selected candidates, both in base tuples.

        The candidates are the placeholder, the size below's base tuples and the population before its diagonal cells
        are dropped.
        """
        return (1 + size.n_required // 4 + n_population) * (1 + size // 4)

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _new_base_tuple_constraints(self) -> list[Constraint]:
        """Return 1 constraint per free lower fine lane: at most 1 new base tuple with its u or its v in that lane."""
        n_candidates = self.population.u.size
        lanes = np.concatenate([self.population.u_lane, self.population.v_lane])
        candidates = self.n_always_selected_candidates + np.concatenate(
            [np.arange(n_candidates), np.arange(n_candidates)]
        )
        return [
            Constraint(int_set=set(candidates[group].tolist()), min_count=0, max_count=1)
            for group in group_indices_by_id(lanes)
        ]

    def _initial_new_selection(self) -> np.ndarray:
        """Return a random starting selection of new candidates, ascending, as indices into the population.

        The candidates are taken in random order, each one whose 2 lower fine lanes are still unused, until the size has
        its new base tuples.

        A candidate is passed over only when 1 of its lanes is used, so 2 lanes stay unused at the end only if no
        candidate lies in their fine cells. At the largest size, when the population holds at least 1 candidate per fine
        cell of the free lanes, every pair of free lanes has a candidate in its fine cell, so the random starting
        selection always uses every free lane.

        Raises:
            MCTuplesConstructionError: If the population runs out before the size has its new base tuples.
        """
        is_used = np.zeros(N_LOWER_FINE_LANES, dtype=bool)
        picked = []
        u_lanes, v_lanes = self.population.u_lane, self.population.v_lane
        for candidate in self.settings.rng.permutation(self.population.u.size).tolist():
            if not (is_used[u_lanes[candidate]] or is_used[v_lanes[candidate]]):
                is_used[u_lanes[candidate]] = is_used[v_lanes[candidate]] = True
                picked.append(candidate)
                if len(picked) == self.n_new_base_tuples:
                    return np.sort(np.array(picked, dtype=np.int64))
        raise MCTuplesConstructionError(
            f"Size {self.size}: only {len(picked)} candidates with unused lanes, "
            f"for {self.n_new_base_tuples} new base tuples."
        )

    def _check_new_selection(self, new_selection: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if a free lower fine lane holds 2 or more values of new base tuples."""
        lanes = np.concatenate([self.population.u_lane[new_selection], self.population.v_lane[new_selection]])
        if np.bincount(lanes).max() > 1:
            raise MCTuplesConstructionError(f"Size {self.size}: a lower fine lane holds 2 or more new values.")
