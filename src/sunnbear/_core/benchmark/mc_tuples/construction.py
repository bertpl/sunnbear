"""`generate_mc_tuples` constructs a nested set of (u, v) tuples that is a Latin hypercube at every size.

The construction builds the sizes bottom-up, the smallest first, and each larger size includes the size
below it, so every size is a prefix of the next.

Each size is a Latin hypercube, as `FreeCellGrid` defines it. Each size is twice the size below it, so the size
below occupies half of the bands on each axis; the new tuples fill the free bands, the half of the bands with no
tuple of the size below, in 2 max-div steps (`construction_steps`):

- **cell selection** (`select_cells`): 1 cell per free band on each axis, where a cell is the crossing of a
  free band along u and a free band along v;
- **refinement** (`refine_within_cells`): 1 tuple inside each selected cell.
"""

import numpy as np

from .construction_settings import MCTuplesConstructionSettings
from .construction_steps import MCTuplesConstructionStep, refine_within_cells, select_cells
from .exceptions import MCTuplesConstructionError
from .free_cell_grid import FreeCellGrid
from .tuples import MCTuples


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
def generate_mc_tuples(t_total_sec: float, n_workers: int = 32, seed: int = 42) -> MCTuples:
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

    Raises:
        ValueError: If `t_total_sec` is below 1 s, or `n_workers` below 1.
        MCTuplesConstructionError: If a size misses a tuple of the size below it or is not a Latin hypercube,
            which can happen when `t_total_sec` is too short for max-div to meet its constraints.
    """
    settings = MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers)
    rng = np.random.default_rng(seed)
    tuples = None
    for k in settings.sizes:
        grid = FreeCellGrid.for_size(k, tuples)
        cells = select_cells(
            grid,
            settings.t_budget_per_solve_sec[k, MCTuplesConstructionStep.CELL_SELECTION],
            settings.n_workers,
            seed,
            rng,
        )
        new_tuples = refine_within_cells(
            grid,
            cells,
            settings.t_budget_per_solve_sec[k, MCTuplesConstructionStep.REFINEMENT],
            settings.n_workers,
            seed,
            rng,
        )
        tuples = new_tuples if tuples is None else tuples.extended_by(new_tuples)
        if not FreeCellGrid.is_latin_hypercube(tuples):
            raise MCTuplesConstructionError(f"Size {k}: the tuples are not a Latin hypercube.")
    assert tuples is not None  # noqa: S101 -- settings.sizes is never empty
    return tuples
