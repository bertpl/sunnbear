"""`MCTuplesSelectionSolve` picks a size's new tuples from its population in the size's first max-div solve.

A fine cell is the crossing of a fine u-lane and a fine v-lane; the outer fine lanes of an axis are its first and its
last fine lane.

The population's candidates all lie in gaps that get new tuples on both axes
(`MCTuplesAxisGapAllocation.eligible_fine_lanes`). Besides the constraint that keeps the tuples of the size
below (`solve`), the constraints are:

- on each axis, each gap holds exactly its allocated number of new tuples;
- a gap that holds more than 1 new tuple holds at most 1 per fine lane, through 1 constraint per fine lane;
- at the smallest size, each of 4 sets of fine cells along the outer fine lanes holds exactly 1 new tuple
  (`MCTuplesSelectionSolve.outer_lane_candidate_sets`), so every size fills both outer fine lanes of each axis, because
  a larger size includes the smallest size's tuples.

max-div starts from a random selection with at most 1 new tuple per fine lane on each axis, which ignores the counts
per gap and the sets along the outer fine lanes; max-div meets both within its first iterations.
"""

from functools import cached_property

import numpy as np
from max_div import Constraint
from scipy.optimize import linear_sum_assignment

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES, MCTuplesSize
from sunnbear._core.utils.grouping import group_indices_by_id

from .allocation import MCTuplesGapAllocation
from .exceptions import MCTuplesConstructionError
from .population import MCTuplesPopulation
from .solve import MCTuplesSolve, MCTuplesSolveSettings

# `EMPTY_CELL_COST` is the cost of pairing a fine u-lane with a fine v-lane through a fine cell without a candidate, in
# the random starting selection; it lies far above the random costs in [0, 1).
EMPTY_CELL_COST = 1e9


# ==================================================================================================
#  MCTuplesSelectionSolve
# ==================================================================================================
class MCTuplesSelectionSolve(MCTuplesSolve):
    """`MCTuplesSelectionSolve` is the max-div solve that picks the new tuples of 1 size from its population.

    Attributes:
        gap_allocation: The allocation of new tuples to the gaps along u and along v, which the solve computes from
            the size below; the population lies in its eligible fine lanes.
    """

    def __init__(
        self,
        n_population: int,
        required_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: MCTuplesSolveSettings,
    ) -> None:
        """Allocate the size's new tuples to gaps, and draw its population of `n_population` candidates.

        The population lies in the eligible fine lanes, and drawing it advances `settings.rng`.
        """
        self.gap_allocation = MCTuplesGapAllocation.of(required_tuple_array, size.n_new)
        population = MCTuplesPopulation.draw(
            n_population,
            self.gap_allocation.u.eligible_fine_lanes,
            self.gap_allocation.v.eligible_fine_lanes,
            settings.rng,
        )
        super().__init__(population, required_tuple_array, size, settings)
        self._u_gap = self.gap_allocation.u.gap_of_fine_lane[self.population.u_lane]
        self._v_gap = self.gap_allocation.v.gap_of_fine_lane[self.population.v_lane]

    @cached_property
    def outer_lane_candidate_sets(self) -> list[np.ndarray]:
        """Return, for each of 4 sets of fine cells along the outer fine lanes, its candidates as population indices.

        The first set is fine u-lane 0 with the fine v-lanes from 1 up to, but not including, `N_FINE_LANES // 2`, which
        leaves out the corner cell; each next set is the previous one rotated by 90 degrees about (0.5, 0.5).

        The 4 sets share no fine cell and contain no corner, so 1 new tuple in each puts 4 distinct tuples in the 4
        outer fine lanes, no 2 of them near the same corner.

        Only the smallest size has these sets, because every larger size includes the smallest size's tuples; a larger
        size gets an empty list.
        """
        if self.size.size_below is not None:
            return []
        else:
            u_lanes, v_lanes = self.population.u_lane, self.population.v_lane
            candidates = []
            for _ in range(4):
                is_in_set = (u_lanes == 0) & (v_lanes >= 1) & (v_lanes < N_FINE_LANES // 2)
                candidates.append(np.flatnonzero(is_in_set))
                # A cell lies in set k + 1 if rotating it back by 90 degrees puts it in set k, so each pass rotates
                # every candidate's lanes back by 90 degrees and tests the first set's condition again.
                u_lanes, v_lanes = v_lanes, N_FINE_LANES - 1 - u_lanes
            return candidates

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _new_tuple_constraints(self) -> list[Constraint]:
        """Return the constraints on the new tuples, as the module docstring lists them."""
        n_required = self.size.n_required
        constraints = []
        for allocation, gap, lane in (
            (self.gap_allocation.u, self._u_gap, self.population.u_lane),
            (self.gap_allocation.v, self._v_gap, self.population.v_lane),
        ):
            for group in group_indices_by_id(gap):
                count = int(allocation.counts[gap[group[0]]])
                constraints.append(
                    Constraint(int_set=set((n_required + group).tolist()), min_count=count, max_count=count)
                )
            in_gaps_of_several = np.flatnonzero(allocation.counts[gap] > 1)
            constraints.extend(
                Constraint(int_set=set((n_required + in_gaps_of_several[group]).tolist()), min_count=0, max_count=1)
                for group in group_indices_by_id(lane[in_gaps_of_several])
            )
        constraints.extend(
            Constraint(int_set=set((n_required + candidates).tolist()), min_count=1, max_count=1)
            for candidates in self.outer_lane_candidate_sets
        )
        return constraints

    def _initial_new_selection(self) -> np.ndarray:
        """Return a random starting selection of new candidates, ascending, as indices into the population.

        A min-cost matching over random costs pairs each fine u-lane with a distinct fine v-lane whose shared fine cell
        holds a candidate; `n_new` of these cells, picked at random, each contribute 1 random candidate. The starting
        selection holds at most 1 new tuple per fine lane, and ignores the counts per gap.

        Raises:
            MCTuplesConstructionError: If fewer fine-lane pairs than new tuples can be formed through cells that hold
                a candidate.
        """
        rng = self.settings.rng
        n_new = self.size.n_new
        fine_u_lanes, u_lane_index = np.unique(self.population.u_lane, return_inverse=True)
        fine_v_lanes, v_lane_index = np.unique(self.population.v_lane, return_inverse=True)
        n_u_lanes, n_v_lanes = fine_u_lanes.size, fine_v_lanes.size
        cells = u_lane_index * n_v_lanes + v_lane_index
        shuffled = rng.permutation(self.population.u.size)
        cells_with_a_candidate, first_in_shuffled = np.unique(cells[shuffled], return_index=True)
        candidate_of_cell = np.full(n_u_lanes * n_v_lanes, -1, dtype=np.int64)
        candidate_of_cell[cells_with_a_candidate] = shuffled[first_in_shuffled]
        costs = rng.random((n_u_lanes, n_v_lanes))
        costs[candidate_of_cell.reshape(n_u_lanes, n_v_lanes) < 0] = EMPTY_CELL_COST
        rows, cols = linear_sum_assignment(costs)
        paired = candidate_of_cell[rows * n_v_lanes + cols]
        paired = paired[paired >= 0]
        if paired.size < n_new:
            raise MCTuplesConstructionError(
                f"Size {self.size}: only {paired.size} fine lanes can be paired through cells with a candidate, for "
                f"{n_new} new tuples."
            )
        return np.sort(rng.choice(paired, size=n_new, replace=False))

    def _check_new_selection(self, new_selection: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if the new tuples break 1 of the constraints in the module docstring."""
        for axis, allocation, gap, lane in (
            ("u", self.gap_allocation.u, self._u_gap, self.population.u_lane),
            ("v", self.gap_allocation.v, self._v_gap, self.population.v_lane),
        ):
            counts = np.bincount(gap[new_selection], minlength=allocation.counts.size)
            n_off = int((counts != allocation.counts).sum())
            if n_off > 0:
                raise MCTuplesConstructionError(
                    f"Size {self.size}: {n_off} gaps along {axis} do not hold their allocated number of new tuples."
                )
            if np.bincount(lane[new_selection]).max() > 1:
                raise MCTuplesConstructionError(f"Size {self.size}: a fine {axis}-lane holds 2 or more new tuples.")
        n_unmet_outer_lane_sets = sum(
            int(np.isin(new_selection, candidates).sum() != 1) for candidates in self.outer_lane_candidate_sets
        )
        if n_unmet_outer_lane_sets > 0:
            raise MCTuplesConstructionError(
                f"Size {self.size}: {n_unmet_outer_lane_sets} of the 4 sets of fine cells along the outer fine lanes "
                "do not hold exactly 1 new tuple."
            )
