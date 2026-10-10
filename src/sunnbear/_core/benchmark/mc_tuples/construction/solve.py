"""`MCTuplesSizeSolve` picks a size's new tuples from its population in 1 max-div solve.

The candidates are the tuples of the size below, which every valid selection keeps, followed by the population's
candidates that lie in a gap that gets new tuples on both axes (`GapAllocation`). The constraints are:

- on each axis, each gap holds exactly its allocated number of new tuples;
- a gap that holds more than 1 new tuple holds at most 1 per fine lane, through 1 constraint per fine lane;
- a weighted constraint keeps every tuple of the size below; it outweighs the others, so max-div meets it first.

The objective is the geomean of 3 gpq terms at `GPQ_LEVEL` over the nearest-neighbor separations: along u, along v
and in squared L2. Since gpq(d²) = gpq(d)², the L2 term weighs as much as the 2 axis terms together.

max-div starts from a random selection with at most 1 new tuple per fine lane on each axis, which ignores the counts
per gap; max-div meets them within its first iterations. max-div weighs its constraints against the objective without
enforcing them, so the selection is checked before it is returned.
"""

import warnings
from dataclasses import dataclass

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric
from max_div.solver import (
    DistanceStorageType,
    ParallelMaxDivSolution,
    ParallelMaxDivSolverBuilder,
    ParallelSolvingWarning,
    Verbosity,
    seconds,
)
from scipy.optimize import linear_sum_assignment

from sunnbear._core.benchmark.mc_tuples.core import GPQ_LEVEL, MCTuplesSize
from sunnbear._core.utils.grouping import group_indices_by_id

from .allocation import GapAllocation
from .exceptions import MCTuplesConstructionError
from .population import MCTuplesPopulation

# The constraint that keeps the tuples of the size below outweighs the other constraints, so max-div meets it first.
INCLUSION_CONSTRAINT_WEIGHT = 10.0

# The cost of pairing a fine u-lane with a fine v-lane through a fine cell without a candidate, in the random starting
# selection; it lies far above the random costs in [0, 1).
EMPTY_CELL_COST = 1e9


# ==================================================================================================
#  MCTuplesSizeSolve
# ==================================================================================================
class MCTuplesSizeSolve:
    """`MCTuplesSizeSolve` is the max-div solve that picks the new tuples of 1 size from its population.

    Attributes:
        population: The size's population of candidate tuples.
        required_tuple_array: The tuples of the size below, as an `(n, 2)` array; empty for the smallest size.
        size: The size under construction.
        gap_allocation: The allocation of new tuples to the gaps along u and along v.
        settings: The construction's settings, the same for every max-div solve.
        candidate_indices: The population's candidates that lie in a gap with new tuples on both axes, as indices into
            the population; max-div picks the new tuples among these.
    """

    def __init__(
        self,
        population: MCTuplesPopulation,
        required_tuple_array: np.ndarray,
        size: MCTuplesSize,
        gap_allocation: GapAllocation,
        settings: "MCTuplesSolveSettings",
    ) -> None:
        """Collect the candidates of `size`: the population's candidates in a gap with new tuples on both axes."""
        self.population = population
        self.required_tuple_array = required_tuple_array
        self.size = size
        self.gap_allocation = gap_allocation
        self.settings = settings
        u_gap = gap_allocation.u.gap_of_fine_lane[population.u_lane]
        v_gap = gap_allocation.v.gap_of_fine_lane[population.v_lane]
        self.candidate_indices = np.flatnonzero((u_gap >= 0) & (v_gap >= 0))
        self._u_gap = u_gap[self.candidate_indices]
        self._v_gap = v_gap[self.candidate_indices]
        self._u_lane = population.u_lane[self.candidate_indices]
        self._v_lane = population.v_lane[self.candidate_indices]

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    def run(self, t_budget_sec: float) -> tuple[np.ndarray, ParallelMaxDivSolution]:
        """Run the solve within `t_budget_sec` and return the new tuples and max-div's solution.

        Returns:
            The new tuples, as an `(n_new, 2)` array of (u, v) values in ascending candidate order, and max-div's
            solution of the solve, with its score checkpoints and timeline.

        Raises:
            MCTuplesConstructionError: If no random starting selection exists, or the selection misses a tuple of the
                size below, holds a number of new tuples in a gap that differs from its allocation, or holds 2 new
                tuples in a fine lane, which can happen when `t_budget_sec` is too short for max-div to meet its
                constraints.
        """
        n_required = self.size.n_required
        gpq = DiversityMetric.gpq_separation(GPQ_LEVEL)
        problem = MaxDivProblem.new(
            # max-div works on a float32 copy; the selected candidates are taken by index.
            np.vstack([self.required_tuple_array, self.population.tuple_array[self.candidate_indices]]).astype(
                np.float32
            ),
            k=int(self.size),
            distance_metric=DistanceMetric.l2s_euclidean_squared(),
            # The geomean of gpq along u, along v, and over the problem's own distance, squared L2.
            diversity_metric=HybridDiversityMetric.geomean_of(
                gpq.over(DistanceMetric.along_axis(0)), gpq.over(DistanceMetric.along_axis(1)), gpq
            ),
            constraints=self._constraints(),
        )
        initial_selection = np.concatenate([np.arange(n_required), n_required + self._initial_new_selection()])
        with warnings.catch_warnings():
            # max-div warns when a short run scales down to 1 worker, and when the workers outnumber the cores; both
            # are deliberate here (the second searches from more seeds).
            warnings.simplefilter("ignore", ParallelSolvingWarning)
            solver = (
                ParallelMaxDivSolverBuilder(problem)
                .with_seed(self.settings.seed)
                .with_workers(seconds(t_budget_sec), self.settings.n_workers)
                .with_end_to_end_budget()
                .with_initial_selection(initial_selection)
                # Every checkpoint also stores its selection, so the solution shows how the selection changed.
                .with_intermediate_selections()
                .with_distance_storage(DistanceStorageType.LAZY)
                .build()
            )
        solution = solver.solve(verbosity=Verbosity.SILENT)
        new = self._validated_new_selection(np.sort(np.asarray(solution.i_selected, dtype=np.int64)))
        return self.population.tuple_array[self.candidate_indices[new]], solution

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _constraints(self) -> list[Constraint]:
        """Return the constraints of the problem, whose points are the size below's tuples and then the candidates.

        On each axis, every gap holds its count of new tuples, and a gap that gets more than 1 new tuple holds at most
        1 per fine lane; a weighted constraint keeps the size below's tuples.
        """
        n_required = self.size.n_required
        constraints = []
        for allocation, gap, lane in (
            (self.gap_allocation.u, self._u_gap, self._u_lane),
            (self.gap_allocation.v, self._v_gap, self._v_lane),
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
        if n_required > 0:
            constraints.append(
                Constraint(
                    int_set=set(range(n_required)),
                    min_count=n_required,
                    max_count=n_required,
                    weight=INCLUSION_CONSTRAINT_WEIGHT,
                )
            )
        return constraints

    def _initial_new_selection(self) -> np.ndarray:
        """Return a random starting selection of new candidates, ascending, as indices into `candidate_indices`.

        A min-cost matching over random costs pairs each fine u-lane with a distinct fine v-lane whose shared fine cell
        holds a candidate; `n_new` of these cells, picked at random, each contribute 1 random candidate. The starting
        selection holds at most 1 new tuple per fine lane, and ignores the counts per gap.

        Raises:
            MCTuplesConstructionError: If fewer fine-lane pairs than new tuples can be formed through cells that hold
                a candidate.
        """
        rng = self.settings.rng
        n_new = int(self.size) - self.size.n_required
        fine_u_lanes, u_lane_index = np.unique(self._u_lane, return_inverse=True)
        fine_v_lanes, v_lane_index = np.unique(self._v_lane, return_inverse=True)
        n_u_lanes, n_v_lanes = fine_u_lanes.size, fine_v_lanes.size
        cells = u_lane_index * n_v_lanes + v_lane_index
        shuffled = rng.permutation(self.candidate_indices.size)
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

    def _validated_new_selection(self, selection: np.ndarray) -> np.ndarray:
        """Return the selected new candidates as indices into `candidate_indices`, after checking the constraints.

        Raises:
            MCTuplesConstructionError: If a tuple of the size below is missing, a gap holds a number of new tuples
                that differs from its allocation, or a fine lane holds 2 or more new tuples.
        """
        n_required = self.size.n_required
        n_missing = n_required - int((selection < n_required).sum())
        if n_missing > 0:
            raise MCTuplesConstructionError(
                f"Size {self.size}: {n_missing} tuples of the size below it are not selected."
            )
        new = selection[selection >= n_required] - n_required
        for axis, allocation, gap, lane in (
            ("u", self.gap_allocation.u, self._u_gap, self._u_lane),
            ("v", self.gap_allocation.v, self._v_gap, self._v_lane),
        ):
            counts = np.bincount(gap[new], minlength=allocation.counts.size)
            n_off = int((counts != allocation.counts).sum())
            if n_off > 0:
                raise MCTuplesConstructionError(
                    f"Size {self.size}: {n_off} gaps along {axis} do not hold their allocated number of new tuples."
                )
            if np.bincount(lane[new]).max() > 1:
                raise MCTuplesConstructionError(f"Size {self.size}: a fine {axis}-lane holds 2 or more new tuples.")
        return new


# ==================================================================================================
#  MCTuplesSolveSettings
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesSolveSettings:
    """`MCTuplesSolveSettings` holds what every max-div solve of a construction shares.

    Attributes:
        n_workers: The number of max-div workers of each solve.
        seed: The seed of each max-div solve.
        rng: The random generator of the construction's own draws: the populations and the starting selections.
    """

    n_workers: int
    seed: int
    rng: np.random.Generator
