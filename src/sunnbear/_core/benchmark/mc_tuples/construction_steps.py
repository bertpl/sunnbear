"""The construction adds the new tuples of 1 size in 2 max-div steps: `select_cells`, then `refine_within_cells`.

- **Cell selection** picks 1 cell of the size's `FreeCellGrid` per free band on each axis, so the size is a
  Latin hypercube; it maximizes the L2 min separation of the cell centers and of the tuples of the size
  below. Every valid choice of cells fills all free bands, so the cell centers have the same coordinates
  along each axis for every choice, and only the L2 separation varies.
- **Refinement** places 1 tuple in each selected cell, chosen from `N_CANDIDATES_PER_CELL` uniform random
  tuples inside the cell, so every value has full float64 precision. It maximizes the smallest of the
  separation fractions along u, along v and in L2 (the objective of `refine_within_cells`).

Both steps require every tuple of the size below to stay selected.
"""

import warnings
from enum import StrEnum

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric
from max_div.solver import ParallelMaxDivSolverBuilder, ParallelSolvingWarning, Verbosity, seconds

from .exceptions import MCTuplesConstructionError
from .free_cell_grid import FreeCellGrid
from .sizes import MCTuplesSize
from .tuples import MCTuples, MCTuplesStats

# The number of random candidate tuples per selected cell in the refinement step.
N_CANDIDATES_PER_CELL = 100

# The constraint that keeps the tuples of the size below outweighs the band constraints, so max-div meets it first.
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
        n_required = 0 if size == min(MCTuplesSize) else size // 2
        n_new = size - n_required
        if self == MCTuplesConstructionStep.CELL_SELECTION:
            return n_new * n_new + n_required
        else:
            return N_CANDIDATES_PER_CELL * n_new + n_required


# ==================================================================================================
#  Steps
# ==================================================================================================
def select_cells(
    grid: FreeCellGrid, t_budget_sec: float, n_workers: int, seed: int, rng: np.random.Generator
) -> np.ndarray:
    """Return the cells of `grid` for the new tuples of its size: 1 per free band along u and 1 per free band along v.

    The selection maximizes the L2 min separation of the selected cell centers and the grid's required tuples.
    Exact constraints keep 1 selected cell per free band. max-div starts from a random Latin hypercube over the
    free bands, which `rng` draws, so the starting selection already meets the band constraints and max-div's
    swaps of 2 cells can exchange their v bands.

    Returns:
        The selected cell indices, ascending.

    Raises:
        MCTuplesConstructionError: If the selection misses a required tuple, or does not hold exactly 1 cell per
            free band, which can happen when `t_budget_sec` is too short for max-div to meet the constraints.
    """
    required_points = _points_of(grid.required_tuples)
    n_required = required_points.shape[0]
    band_constraints = [
        Constraint(int_set=set((n_required + band_cells).tolist()), min_count=1, max_count=1)
        for band_cells in grid.band_cells()
    ]
    problem = MaxDivProblem.new(
        # max-div works on a float32 copy; the selected cells are taken by index.
        np.vstack([required_points, grid.cell_centers]).astype(np.float32),
        k=grid.size,
        distance_metric=DistanceMetric.l2_euclidean(),
        diversity_metric=DiversityMetric.MIN_SEPARATION,
        constraints=band_constraints + _inclusion_constraints(n_required),
    )
    initial_cells = grid.latin_hypercube_cells(rng.permutation(grid.free_v_bands.size))
    initial_selection = np.concatenate([np.arange(n_required), n_required + initial_cells])
    selection = _solve(problem, initial_selection, t_budget_sec, n_workers, seed)
    cells = _new_candidate_indices(selection, n_required, grid.size)
    if not grid.is_one_per_free_band(cells):
        raise MCTuplesConstructionError(f"Size {grid.size}: the selected cells do not hold exactly 1 per free band.")
    return cells


def refine_within_cells(
    grid: FreeCellGrid, cells: np.ndarray, t_budget_sec: float, n_workers: int, seed: int, rng: np.random.Generator
) -> MCTuples:
    """Return 1 new tuple in each of `cells`, chosen from `N_CANDIDATES_PER_CELL` random tuples inside the cell.

    The objective maximizes the smaller of 2 weighted min separations:

    - **along the axes**: `size - 1` times the min separation under the L-minus-infinity distance
      `min(|Δu|, |Δv|)`, which equals the smaller of the min separations along u and along v;
    - **in the square**: `√size - 1` times the min separation under L2.

    Each weight is the inverse of the spacing of `size` evenly spaced tuples, along an axis or on a square grid,
    so max-div raises the smallest of the 3 separation fractions of `MCTuplesStats`. The separations along an
    axis matter because u and v each set a separate parameter of a test function.

    No constraint keeps 1 tuple per cell; the objective does: 2 tuples in 1 cell would lie less than 1 band width
    apart on each axis, which lowers the separation along the axes.

    Returns:
        The new tuples, in the order of `cells`.

    Raises:
        MCTuplesConstructionError: If the selection misses a required tuple or does not hold 1 new tuple per cell.
    """
    required_points = _points_of(grid.required_tuples)
    n_required = required_points.shape[0]
    candidates = grid.sample_in_cells(cells, N_CANDIDATES_PER_CELL, rng)
    problem = MaxDivProblem.new(
        # max-div works on a float32 copy; the selected tuples are taken from the float64 candidates by index.
        np.vstack([required_points, candidates.reshape(-1, 2)]).astype(np.float32),
        k=grid.size,
        distance_metric=DistanceMetric.l2_euclidean(),
        diversity_metric=HybridDiversityMetric.min_of(
            DiversityMetric.MIN_SEPARATION.over(DistanceMetric.l_minus_inf()),
            DiversityMetric.MIN_SEPARATION.over(DistanceMetric.l2_euclidean()),
            weights=(MCTuplesStats.inverse_axis_spacing(grid.size), MCTuplesStats.inverse_grid_spacing(grid.size)),
        ),
        constraints=_inclusion_constraints(n_required),
    )
    # max-div starts from the candidate nearest to each cell's center.
    centers = grid.cell_centers[cells]
    nearest_candidates = np.argmin(np.abs(candidates - centers[:, None, :]).sum(axis=-1), axis=1)
    initial_selection = np.concatenate(
        [np.arange(n_required), n_required + np.arange(cells.size) * N_CANDIDATES_PER_CELL + nearest_candidates]
    )
    selection = _solve(problem, initial_selection, t_budget_sec, n_workers, seed)
    selected_cells, selected_candidates = np.divmod(
        _new_candidate_indices(selection, n_required, grid.size), N_CANDIDATES_PER_CELL
    )
    if np.unique(selected_cells).size != cells.size:
        raise MCTuplesConstructionError(f"Size {grid.size}: the refinement does not hold 1 new tuple per cell.")
    points = candidates[selected_cells, selected_candidates]
    return MCTuples(points[:, 0], points[:, 1])


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _points_of(tuples: MCTuples | None) -> np.ndarray:
    """Return the points of `tuples`, or an empty `(0, 2)` array for None."""
    return np.empty((0, 2)) if tuples is None else tuples.points


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


def _solve(
    problem: MaxDivProblem, initial_selection: np.ndarray, t_budget_sec: float, n_workers: int, seed: int
) -> np.ndarray:
    """Return max-div's selection for `problem`, started from `initial_selection`, as sorted candidate indices."""
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
            .build()
        )
    solution = solver.solve(verbosity=Verbosity.SILENT)
    return np.sort(np.asarray(solution.i_selected, dtype=np.int64))


def _new_candidate_indices(selection: np.ndarray, n_required: int, size: int) -> np.ndarray:
    """Return the selected candidates that are not required, as indices relative to the first non-required candidate.

    Raises:
        MCTuplesConstructionError: If the selection misses a required candidate.
    """
    n_missing = n_required - int((selection < n_required).sum())
    if n_missing > 0:
        raise MCTuplesConstructionError(f"Size {size}: {n_missing} tuples of the size below it are not selected.")
    return selection[selection >= n_required] - n_required
