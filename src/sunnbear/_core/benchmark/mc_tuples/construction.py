"""`generate_mc_tuples` constructs a nested set of (u, v) tuples that holds exactly 1 tuple per lane at every size.

The construction builds the sizes bottom-up, the smallest first, and each larger size includes the size
below it, so every size is a prefix of the next.

Each size first fixes the u and v values that its new tuples aim for, and cuts each axis into lanes around all
of its values, as `LaneGrid` defines them. The new tuples go in the cells where a new u lane crosses a new v
lane, in 2 max-div steps (`construction_steps`):

- **cell selection** (`select_cells`): 1 cell per new lane on each axis;
- **refinement** (`refine_within_cells`): 1 tuple inside each selected cell.

Each finished solve is reported as an `MCTuplesSolveReport` to the caller's `on_solve`, so that a long
construction can show its progress and store its points and max-div's solutions as it goes.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Self

import numpy as np
from max_div.solver import ParallelMaxDivSolution

from .construction_settings import MCTuplesConstructionSettings
from .construction_steps import MCTuplesConstructionStep, refine_within_cells, select_cells
from .exceptions import MCTuplesConstructionError
from .lane_grid import LaneGrid
from .sizes import MCTuplesSize
from .tuples import MCTuples


# ==================================================================================================
#  MCTuplesSolveReport
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesSolveReport:
    """`MCTuplesSolveReport` describes 1 finished max-div solve of a construction, for progress reports and inspection.

    Attributes:
        size: The size whose new tuples the solve places.
        step: The construction step of the solve.
        t_budget_sec: The solve's wall-clock budget.
        t_wall_sec: The solve's wall-clock time: the budget, plus max-div's start and stop and the step's checks.
        points: The size's points after the solve, the size below first, as a `(size, 2)` array of (u, v) values:

            - after cell selection, the points of the selected cells, which can lie on the edges of the unit square;
            - after refinement, the size's tuple set.
        solution: max-div's solution of the solve, with its score checkpoints and timeline.
    """

    size: MCTuplesSize
    step: MCTuplesConstructionStep
    t_budget_sec: float
    t_wall_sec: float
    points: np.ndarray
    solution: ParallelMaxDivSolution

    @classmethod
    def from_start_time(
        cls,
        t_start: float,
        size: MCTuplesSize,
        step: MCTuplesConstructionStep,
        t_budget_sec: float,
        points: np.ndarray,
        solution: ParallelMaxDivSolution,
    ) -> Self:
        """Return the report of a solve that started at `t_start` (`time.perf_counter`) and ended now."""
        return cls(size, step, t_budget_sec, time.perf_counter() - t_start, points, solution)


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
def generate_mc_tuples(
    t_total_sec: float,
    n_workers: int = 32,
    seed: int = 42,
    on_solve: Callable[[MCTuplesSolveReport], None] | None = None,
) -> MCTuples:
    """Construct a nested Monte Carlo tuple set in about `t_total_sec` s; its first `k` tuples form size `k`.

    The construction runs 2 max-div solves per size, and splits `t_total_sec` over them as
    `MCTuplesConstructionSettings.from_total_time` describes:

    - from 60 s up, the construction builds every size of `MCTuplesSize` with all `n_workers` workers;
    - below 60 s, it builds fewer sizes, down to the 2 smallest, with fewer workers, for short runs such as tests;
      the returned set then ends at the largest size built.

    `t_total_sec` covers only the solves; other steps take extra time:

    - drawing the random tuples that the solves choose from, and building each solve's problem;
    - checking each size;
    - compiling each max-div function that the solves use, on its first run after an install; compiling them
      all takes seconds, and numba caches the compiled code for later runs.

    A rerun gives a set of equivalent quality, not the same set, because max-div's parallel solver
    runs on a wall-clock budget.

    Args:
        t_total_sec: The total wall-clock time of the solves, at least 1 s.
        n_workers: The number of max-div workers per solve when `t_total_sec` is 60 s or more; more workers search from
            more seeds, and may exceed the number of cores.
        seed: The seed of every random draw and of every max-div solve.
        on_solve: Called with an `MCTuplesSolveReport` after each of the 2 solves of every size, e.g. to print the
            progress of a long construction or to store its points and solutions; None reports nothing.

    Raises:
        ValueError: If `t_total_sec` is below 1 s, or `n_workers` below 1.
        MCTuplesConstructionError: If a size misses a tuple of the size below it or does not hold exactly 1 tuple
            per lane, which can happen when `t_total_sec` is too short for max-div to meet its constraints.
    """
    settings = MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers)
    rng = np.random.default_rng(seed)
    tuples = None
    for k in settings.sizes:
        grid = LaneGrid.for_size(k, tuples)

        # --- cell selection ---------------------
        step = MCTuplesConstructionStep.CELL_SELECTION
        t_budget_sec = settings.t_budget_per_solve_sec[k, step]
        t_start = time.perf_counter()
        cells, solution = select_cells(grid, t_budget_sec, settings.n_workers, seed, rng)
        points_after_cell_selection = grid.points_with_cells(cells)
        _report_solve(
            on_solve,
            MCTuplesSolveReport.from_start_time(t_start, k, step, t_budget_sec, points_after_cell_selection, solution),
        )

        # --- refinement -------------------------
        step = MCTuplesConstructionStep.REFINEMENT
        t_budget_sec = settings.t_budget_per_solve_sec[k, step]
        t_start = time.perf_counter()
        new_tuples, solution = refine_within_cells(grid, cells, t_budget_sec, settings.n_workers, seed, rng)
        tuples = new_tuples if tuples is None else tuples.extended_by(new_tuples)
        if not grid.is_one_per_lane(tuples):
            raise MCTuplesConstructionError(f"Size {k}: the tuples do not hold exactly 1 per lane.")
        _report_solve(
            on_solve, MCTuplesSolveReport.from_start_time(t_start, k, step, t_budget_sec, tuples.points, solution)
        )
    assert tuples is not None  # noqa: S101 -- settings.sizes is never empty
    return tuples


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _report_solve(on_solve: Callable[[MCTuplesSolveReport], None] | None, report: MCTuplesSolveReport) -> None:
    """Pass `report` to `on_solve`, if there is one."""
    if on_solve is not None:
        on_solve(report)
