"""The new tuples of 1 size come from 2 max-div steps: `MCTuplesCellSelectionStep`, then `MCTuplesRefinementStep`.

- **Cell selection** picks cells of the size's `LaneGrid`, where a cell is the crossing of a new u lane and a
  new v lane and is represented by the tuple (new u value of its u lane, new v value of its v lane); it picks 1
  cell per new lane on each axis. Every valid choice of cells uses every new lane, so the sets of u values and
  v values are the same for every choice; the step therefore maximizes only the L2 min separation of the cells'
  tuples and of the tuples of the size below.
- **Refinement** places 1 tuple in each selected cell, chosen from `N_CANDIDATES_PER_CELL` uniform random
  float64 tuples inside the cell; max-div compares float32 copies, and the chosen tuple keeps its float64
  values. It maximizes the min separation under max-div's `l2_and_projections` distance, configured for `size`
  tuples; maximizing it raises the smallest of the 3 separation fractions of `MCTuplesStats`: along u, along v and
  in L2.
"""

import time
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric
from max_div.solver import (
    ParallelMaxDivSolution,
    ParallelMaxDivSolverBuilder,
    ParallelSolvingWarning,
    Verbosity,
    seconds,
)

from .construction_step_results import MCTuplesCellSelectionResult, MCTuplesRefinementResult, MCTuplesStepResult
from .exceptions import MCTuplesConstructionError
from .lane_grid import LaneGrid
from .sizes import MCTuplesSize
from .tuples import MCTuples

# The number of random candidate tuples per selected cell in the refinement step. At this pool size, the L2
# fraction is already the smallest of the 3 fractions in the objective, and cell selection, not refinement, sets
# the L2 separation; a larger pool would only leave refinement fewer iterations within its budget.
N_CANDIDATES_PER_CELL = 256

# The constraint that keeps the tuples of the size below outweighs the lane constraints, so max-div meets it first.
INCLUSION_CONSTRAINT_WEIGHT = 10.0


# ==================================================================================================
#  MCTuplesSolveSettings
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesSolveSettings:
    """`MCTuplesSolveSettings` holds what every max-div solve of a construction shares.

    Attributes:
        n_workers: The number of max-div workers of each solve.
        seed: The seed of each max-div solve.
        rng: The random generator of the steps' own draws, such as a starting selection or the candidates.
    """

    n_workers: int
    seed: int
    rng: np.random.Generator

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def for_seed(cls, n_workers: int, seed: int) -> "MCTuplesSolveSettings":
        """Return the settings whose max-div solves and random draws all derive from `seed`."""
        return cls(n_workers=n_workers, seed=seed, rng=np.random.default_rng(seed))


# ==================================================================================================
#  MCTuplesStep
# ==================================================================================================
class MCTuplesStep(ABC):
    """`MCTuplesStep` is 1 max-div solve toward the new tuples of a size; its subclasses are the 2 steps.

    A step is built for 1 size, from the size's lane grid. Its candidates are the tuples of the size below, which
    every valid selection keeps, followed by the step's own new candidates; max-div selects as many as the size
    holds. The base class runs the max-div solve in `_solve`. A subclass:

    - supplies its new candidates, objective, constraints and starting selection;
    - validates what max-div selected among its own candidates.

    Attributes:
        grid: The lane grid of the size, with the tuples of the size below.
        settings: The settings that every max-div solve of the construction shares.
    """

    def __init__(self, grid: LaneGrid, settings: MCTuplesSolveSettings) -> None:
        """Build the step for the size of `grid`."""
        self.grid = grid
        self.settings = settings

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    @classmethod
    @abstractmethod
    def n_candidates(cls, size: int) -> int:
        """Return the number of candidates of this step for `size`, the tuples of the size below included."""

    @abstractmethod
    def run(self, t_budget_sec: float) -> MCTuplesStepResult:
        """Run the step's max-div solve within `t_budget_sec` and return its result.

        Raises:
            MCTuplesConstructionError: If max-div's selection breaks the step's constraints, which can happen when
                `t_budget_sec` is too short for max-div to meet them.
        """

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _solve(
        self,
        new_candidate_array: np.ndarray,
        diversity_metric: DiversityMetric,
        distance_metric: DistanceMetric,
        constraints: list[Constraint],
        initial_new_selection: np.ndarray,
        t_budget_sec: float,
    ) -> tuple[np.ndarray, ParallelMaxDivSolution]:
        """Run max-div over the tuples of the size below and `new_candidate_array`; return the selected new candidates.

        The tuples of the size below come first among the candidates, and a weighted constraint asks max-div to
        keep all of those tuples. The other arguments:

        - the objective is `diversity_metric`, computed from `distance_metric` between pairs of tuples;
        - `constraints` holds the step's own constraints;
        - the indices in `constraints` and in `initial_new_selection` count rows of `new_candidate_array`.

        Returns:
            The indices of the selected new candidates, ascending, relative to `new_candidate_array`, and max-div's
            solution of the solve.

        Raises:
            MCTuplesConstructionError: If the selection misses a tuple of the size below.
        """
        n_required = self.grid.n_required
        problem = MaxDivProblem.new(
            # max-div works on a float32 copy; the selected candidates are taken by index.
            np.vstack([self.grid.required_tuple_array, new_candidate_array]).astype(np.float32),
            k=self.grid.size,
            distance_metric=distance_metric,
            diversity_metric=diversity_metric,
            constraints=[
                *(
                    replace(constraint, int_set={n_required + i for i in constraint.int_set})
                    for constraint in constraints
                ),
                *self._inclusion_constraints(n_required),
            ],
        )
        initial_selection = np.concatenate([np.arange(n_required), n_required + initial_new_selection])
        selection, solution = self._run_max_div(problem, initial_selection, t_budget_sec)
        n_missing = n_required - int((selection < n_required).sum())
        if n_missing > 0:
            raise MCTuplesConstructionError(
                f"Size {self.grid.size}: {n_missing} tuples of the size below it are not selected."
            )
        return selection[selection >= n_required] - n_required, solution

    def _run_max_div(
        self, problem: MaxDivProblem, initial_selection: np.ndarray, t_budget_sec: float
    ) -> tuple[np.ndarray, ParallelMaxDivSolution]:
        """Return max-div's sorted selection for `problem`, started from `initial_selection`, and its solution."""
        with warnings.catch_warnings():
            # max-div warns when a short run scales down to 1 worker, and when the workers outnumber the
            # cores; both are deliberate here (the second searches from more seeds).
            warnings.simplefilter("ignore", ParallelSolvingWarning)
            solver = (
                ParallelMaxDivSolverBuilder(problem)
                .with_seed(self.settings.seed)
                .with_workers(seconds(t_budget_sec), self.settings.n_workers)
                .with_end_to_end_budget()
                .with_initial_selection(initial_selection)
                # Every checkpoint also stores its selection, so the solution shows how the selection changed.
                .with_intermediate_selections()
                .build()
            )
        solution = solver.solve(verbosity=Verbosity.SILENT)
        return np.sort(np.asarray(solution.i_selected, dtype=np.int64)), solution

    @staticmethod
    def _inclusion_constraints(n_required: int) -> list[Constraint]:
        """Return the constraint that the first `n_required` candidates are all selected, or none if there are none."""
        if n_required == 0:
            return []
        else:
            return [
                Constraint(
                    int_set=set(range(n_required)),
                    min_count=n_required,
                    max_count=n_required,
                    weight=INCLUSION_CONSTRAINT_WEIGHT,
                )
            ]


# ==================================================================================================
#  MCTuplesCellSelectionStep
# ==================================================================================================
class MCTuplesCellSelectionStep(MCTuplesStep):
    """`MCTuplesCellSelectionStep` picks the cells for the new tuples of a size: 1 per new lane along u and along v.

    The selection maximizes the L2 min separation of the selected cells' tuples and the tuples of the size below.
    A constraint per new lane asks for exactly 1 selected cell in it; max-div weighs the constraints against the
    objective without enforcing them, so the selection is checked before it is returned.

    max-div starts from random cells that pair each new u lane with a different new v lane, so the starting
    selection already meets the lane constraints; from there, max-div reaches other valid selections by
    exchanging the v lanes of 2 selected cells.
    """

    @classmethod
    def n_candidates(cls, size: int) -> int:
        """Return the number of cells of `size`, plus the tuples of the size below."""
        n_required = MCTuplesSize(size).n_required
        n_new = size - n_required
        return n_new * n_new + n_required

    def run(self, t_budget_sec: float) -> MCTuplesCellSelectionResult:
        """Select the cells within `t_budget_sec` and return them, with the size's tuples as they stand after the step.

        Raises:
            MCTuplesConstructionError: If the selection misses a tuple of the size below, or does not hold exactly 1
                cell per new lane.
        """
        t_start = time.perf_counter()
        grid = self.grid
        lane_constraints = [
            Constraint(int_set=set(lane_cells.tolist()), min_count=1, max_count=1) for lane_cells in grid.lane_cells()
        ]
        cells, solution = self._solve(
            grid.cell_tuple_array,
            DiversityMetric.MIN_SEPARATION,
            DistanceMetric.l2_euclidean(),
            lane_constraints,
            grid.random_one_per_new_lane_cells(self.settings.rng),
            t_budget_sec,
        )
        if not grid.is_one_per_new_lane(cells):
            raise MCTuplesConstructionError(f"Size {grid.size}: the selected cells do not hold exactly 1 per new lane.")
        return MCTuplesCellSelectionResult(
            size=MCTuplesSize(grid.size),
            t_budget_sec=t_budget_sec,
            t_wall_sec=time.perf_counter() - t_start,
            tuple_array=grid.required_and_cell_tuple_array(cells),
            solution=solution,
            cells=cells,
        )


# ==================================================================================================
#  MCTuplesRefinementStep
# ==================================================================================================
class MCTuplesRefinementStep(MCTuplesStep):
    """`MCTuplesRefinementStep` places 1 new tuple in each selected cell, chosen from random tuples inside the cell.

    The candidates are `N_CANDIDATES_PER_CELL` uniform random tuples per cell. The objective is the min separation
    under max-div's `l2_and_projections` distance, configured for `size` tuples, which takes the smaller of 2
    distances per pair:

    - **along the axes**: the L-minus-infinity distance `min(|Δu|, |Δv|)`, which equals the smaller of the gaps
      along u and along v;
    - **in the square**: the L2 distance scaled by `(√size - 1) / (size - 1)`, the ratio of the spacings of `size`
      evenly spaced tuples along an axis and on a square grid.

    With that scale, max-div raises the smallest of the 3 separation fractions of `MCTuplesStats`. The separations
    along an axis matter because u and v each set a separate parameter of a test function.

    No constraint keeps 1 tuple per cell; the objective does: 2 tuples in 1 cell would lie less than a lane
    width apart on each axis, which lowers the separation along the axes. max-div starts from the candidate
    nearest to each cell's tuple, which is cell selection's optimized position.

    Attributes:
        cells: The selected cells, from cell selection; the new tuples come in the same order.
    """

    def __init__(self, grid: LaneGrid, cells: np.ndarray, settings: MCTuplesSolveSettings) -> None:
        """Build the step for the size of `grid`, placing the new tuples in `cells`."""
        super().__init__(grid, settings)
        self.cells = cells

    @classmethod
    def n_candidates(cls, size: int) -> int:
        """Return `size`'s candidate count: `N_CANDIDATES_PER_CELL` per new tuple plus the tuples of the size below."""
        n_required = MCTuplesSize(size).n_required
        return N_CANDIDATES_PER_CELL * (size - n_required) + n_required

    def run(self, t_budget_sec: float) -> MCTuplesRefinementResult:
        """Place the new tuples within `t_budget_sec` and return the whole size's tuples.

        Raises:
            MCTuplesConstructionError: If the selection misses a tuple of the size below, does not hold 1 new
                tuple per cell, or leaves a lane of the size without exactly 1 tuple.
        """
        t_start = time.perf_counter()
        grid, cells = self.grid, self.cells
        candidates = grid.sample_in_cells(cells, N_CANDIDATES_PER_CELL, self.settings.rng)
        selected_cell_tuple_array = grid.cell_tuple_array[cells]
        nearest_candidates = np.argmin(np.abs(candidates - selected_cell_tuple_array[:, None, :]).sum(axis=-1), axis=1)
        new_selection, solution = self._solve(
            candidates.reshape(-1, 2),
            DiversityMetric.MIN_SEPARATION,
            DistanceMetric.l2_and_projections(k=grid.size),
            [],
            np.arange(cells.size) * N_CANDIDATES_PER_CELL + nearest_candidates,
            t_budget_sec,
        )
        i_selected_cells, i_selected_candidates = np.divmod(new_selection, N_CANDIDATES_PER_CELL)
        if np.unique(i_selected_cells).size != cells.size:
            raise MCTuplesConstructionError(f"Size {grid.size}: the refinement does not hold 1 new tuple per cell.")
        tuple_array = np.vstack([grid.required_tuple_array, candidates[i_selected_cells, i_selected_candidates]])
        tuples = MCTuples(tuple_array[:, 0], tuple_array[:, 1])
        if not grid.is_one_per_lane(tuples):
            raise MCTuplesConstructionError(f"Size {grid.size}: the tuples do not hold exactly 1 per lane.")
        return MCTuplesRefinementResult(
            size=MCTuplesSize(grid.size),
            t_budget_sec=t_budget_sec,
            t_wall_sec=time.perf_counter() - t_start,
            tuple_array=tuple_array,
            solution=solution,
            tuples=tuples,
        )
