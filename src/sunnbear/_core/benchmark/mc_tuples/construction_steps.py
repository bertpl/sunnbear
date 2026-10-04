"""The construction adds the new tuples of 1 size in 2 max-div steps: `select_cells`, then `refine_within_cells`.

- **Cell selection** picks cells of the size's `LaneGrid`, where a cell is the crossing of a new u lane and a
  new v lane and is represented by the tuple (new u value of its u lane, new v value of its v lane); it picks 1
  cell per new lane on each axis. Every valid choice of cells uses every new lane, so the sets of u values and
  v values are the same for every choice; the step therefore maximizes only the L2 min separation of the cells'
  tuples and of the tuples of the size below.
- **Refinement** places 1 tuple in each selected cell, chosen from `N_CANDIDATES_PER_CELL` uniform random
  float64 tuples inside the cell; max-div compares float32 copies, and the chosen tuple keeps its float64
  values. It maximizes the smallest of the 3 separation fractions of `MCTuplesStats`: along u, along v and in
  L2 (the objective of `refine_within_cells`).

Both steps require every tuple of the size below to stay selected, and both return max-div's solution next to
their result, so that a caller can keep the solution's score checkpoints for inspection.
"""

import warnings
from enum import StrEnum

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric
from max_div.solver import (
    ParallelMaxDivSolution,
    ParallelMaxDivSolverBuilder,
    ParallelSolvingWarning,
    Verbosity,
    seconds,
)

from .exceptions import MCTuplesConstructionError
from .lane_grid import LaneGrid
from .sizes import MCTuplesSize
from .tuples import MCTuples, MCTuplesStats

# The number of random candidate tuples per selected cell in the refinement step. At this pool size, the L2
# fraction is already the smallest of the 3 fractions in the objective, and cell selection, not refinement, sets
# the L2 separation; a larger pool would only leave refinement fewer iterations within its budget.
N_CANDIDATES_PER_CELL = 256

# The constraint that keeps the tuples of the size below outweighs the lane constraints, so max-div meets it first.
INCLUSION_CONSTRAINT_WEIGHT = 10.0


# ==================================================================================================
#  MCTuplesConstructionStep
# ==================================================================================================
class MCTuplesConstructionStep(StrEnum):
    """`MCTuplesConstructionStep` is 1 of the 2 max-div steps that add the new tuples of a size."""

    CELL_SELECTION = "cell_selection"
    REFINEMENT = "refinement"

    def n_candidates(self, size: int) -> int:
        """Return the number of candidates of this step for `size`, the tuples of the size below included."""
        n_required = MCTuplesSize(size).n_required
        n_new = size - n_required
        if self == MCTuplesConstructionStep.CELL_SELECTION:
            return n_new * n_new + n_required
        else:
            return N_CANDIDATES_PER_CELL * n_new + n_required


# ==================================================================================================
#  Steps
# ==================================================================================================
def select_cells(
    grid: LaneGrid, t_budget_sec: float, n_workers: int, seed: int, rng: np.random.Generator
) -> tuple[np.ndarray, ParallelMaxDivSolution]:
    """Return the cells of `grid` for the new tuples of its size: 1 per new lane along u and 1 per new lane along v.

    The selection maximizes the L2 min separation of the selected cells' tuples and the tuples of the size below
    (`grid.required_tuples`). A constraint per new lane asks for exactly 1 selected cell in it; max-div weighs
    the constraints against the objective without enforcing them, so the selection is checked before it is
    returned.

    max-div starts from random cells, drawn with `rng`, that pair each new u lane with a different new v lane,
    so the starting selection already meets the lane constraints; from there, max-div reaches other valid
    selections by exchanging the v lanes of 2 selected cells. `seed` seeds max-div's solve.

    Returns:
        The selected cell indices, ascending, and max-div's solution of the solve.

    Raises:
        MCTuplesConstructionError: If the selection misses a required tuple, or does not hold exactly 1 cell per
            new lane, which can happen when `t_budget_sec` is too short for max-div to meet the constraints.
    """
    required_tuple_array = grid.required_tuple_array
    n_required = required_tuple_array.shape[0]
    lane_constraints = [
        Constraint(int_set=set((n_required + lane_cells).tolist()), min_count=1, max_count=1)
        for lane_cells in grid.lane_cells()
    ]
    problem = MaxDivProblem.new(
        # max-div works on a float32 copy; the selected cells are taken by index.
        np.vstack([required_tuple_array, grid.cell_tuple_array]).astype(np.float32),
        k=grid.size,
        distance_metric=DistanceMetric.l2_euclidean(),
        diversity_metric=DiversityMetric.MIN_SEPARATION,
        constraints=lane_constraints + _inclusion_constraints(n_required),
    )
    initial_cells = grid.random_one_per_new_lane_cells(rng)
    initial_selection = np.concatenate([np.arange(n_required), n_required + initial_cells])
    selection, solution = _run_max_div(problem, initial_selection, t_budget_sec, n_workers, seed)
    cells = _indices_among_new_candidates(selection, n_required, grid.size)
    if not grid.is_one_per_new_lane(cells):
        raise MCTuplesConstructionError(f"Size {grid.size}: the selected cells do not hold exactly 1 per new lane.")
    return cells, solution


def refine_within_cells(
    grid: LaneGrid, cells: np.ndarray, t_budget_sec: float, n_workers: int, seed: int, rng: np.random.Generator
) -> tuple[MCTuples, ParallelMaxDivSolution]:
    """Return 1 new tuple in each of `cells`, chosen from `N_CANDIDATES_PER_CELL` random tuples inside the cell.

    `rng` draws the candidates; `seed` seeds max-div's solve.

    The objective maximizes the smaller of 2 weighted min separations:

    - **along the axes**: `size - 1` times the min separation under the L-minus-infinity distance
      `min(|Δu|, |Δv|)`, which equals the smaller of the min separations along u and along v;
    - **in the square**: `√size - 1` times the min separation under L2.

    Each weight is the inverse of the spacing of `size` evenly spaced tuples, along an axis or on a square grid,
    so max-div raises the smallest of the 3 separation fractions of `MCTuplesStats`. The separations along an
    axis matter because u and v each set a separate parameter of a test function.

    No constraint keeps 1 tuple per cell; the objective does: 2 tuples in 1 cell would lie less than a lane
    width apart on each axis, which lowers the separation along the axes.

    Returns:
        The new tuples, in the order of `cells`, and max-div's solution of the solve.

    Raises:
        MCTuplesConstructionError: If the selection misses a required tuple or does not hold 1 new tuple per cell,
            which can happen when `t_budget_sec` is too short for max-div to meet them.
    """
    required_tuple_array = grid.required_tuple_array
    n_required = required_tuple_array.shape[0]
    candidates = grid.sample_in_cells(cells, N_CANDIDATES_PER_CELL, rng)
    problem = MaxDivProblem.new(
        # max-div works on a float32 copy; the selected tuples are taken from the float64 candidates by index.
        np.vstack([required_tuple_array, candidates.reshape(-1, 2)]).astype(np.float32),
        k=grid.size,
        distance_metric=DistanceMetric.l2_euclidean(),
        diversity_metric=HybridDiversityMetric.min_of(
            DiversityMetric.MIN_SEPARATION.over(DistanceMetric.l_minus_inf()),
            DiversityMetric.MIN_SEPARATION.over(DistanceMetric.l2_euclidean()),
            weights=(MCTuplesStats.inverse_axis_spacing(grid.size), MCTuplesStats.inverse_grid_spacing(grid.size)),
        ),
        constraints=_inclusion_constraints(n_required),
    )
    # max-div starts from the candidate nearest to each cell's tuple, the position that cell selection optimized.
    cell_tuple_array = grid.cell_tuple_array[cells]
    nearest_candidates = np.argmin(np.abs(candidates - cell_tuple_array[:, None, :]).sum(axis=-1), axis=1)
    initial_selection = np.concatenate(
        [np.arange(n_required), n_required + np.arange(cells.size) * N_CANDIDATES_PER_CELL + nearest_candidates]
    )
    selection, solution = _run_max_div(problem, initial_selection, t_budget_sec, n_workers, seed)
    selected_cells, selected_candidates = np.divmod(
        _indices_among_new_candidates(selection, n_required, grid.size), N_CANDIDATES_PER_CELL
    )
    if np.unique(selected_cells).size != cells.size:
        raise MCTuplesConstructionError(f"Size {grid.size}: the refinement does not hold 1 new tuple per cell.")
    tuple_array = candidates[selected_cells, selected_candidates]
    return MCTuples(tuple_array[:, 0], tuple_array[:, 1]), solution


# ==================================================================================================
#  Helpers
# ==================================================================================================
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


def _run_max_div(
    problem: MaxDivProblem, initial_selection: np.ndarray, t_budget_sec: float, n_workers: int, seed: int
) -> tuple[np.ndarray, ParallelMaxDivSolution]:
    """Return max-div's sorted selection for `problem`, started from `initial_selection`, and its solution."""
    with warnings.catch_warnings():
        # max-div warns when a short run scales down to 1 worker, and when the workers outnumber the
        # cores; both are deliberate here (the second searches from more seeds).
        warnings.simplefilter("ignore", ParallelSolvingWarning)
        solver = (
            ParallelMaxDivSolverBuilder(problem)
            .with_seed(seed)
            .with_workers(seconds(t_budget_sec), n_workers)
            .with_end_to_end_budget()
            .with_initial_selection(initial_selection)
            # Every checkpoint also stores its selection, so the solution shows how the selection changed.
            .with_intermediate_selections()
            .build()
        )
    solution = solver.solve(verbosity=Verbosity.SILENT)
    return np.sort(np.asarray(solution.i_selected, dtype=np.int64)), solution


def _indices_among_new_candidates(selection: np.ndarray, n_required: int, size: int) -> np.ndarray:
    """Return the selected candidates that are not required, as indices relative to the first non-required candidate.

    Raises:
        MCTuplesConstructionError: If the selection misses a required candidate.
    """
    n_missing = n_required - int((selection < n_required).sum())
    if n_missing > 0:
        raise MCTuplesConstructionError(f"Size {size}: {n_missing} tuples of the size below it are not selected.")
    return selection[selection >= n_required] - n_required
