"""`generate_mc_tuples` constructs a nested set of (u, v) tuples, spread as evenly as max-div can make it.

The construction selects each size with max-div from a uniform random population of candidate tuples:

- **objective**: maximize the geometric mean of 3 min separations, each the smallest distance
  between 2 selected tuples: in the square (L2), along u and along v; the 2 separations along an
  axis keep the tuples apart on each axis alone, because u and v each set a separate parameter of
  a test function;
- **inclusion**: the sizes are built bottom-up, the smallest first, and each larger size is
  constrained to include the size below it, so every size is a prefix of the next;
- **bins**: bin constraints cut each axis into `N_BINS` equal bins, and keep the number of a
  size's tuples in each bin within 1 of `size / N_BINS`.
"""

import numpy as np

from .construction_settings import FULL_POPULATION_SIZE, MCTuplesConstructionSettings
from .exceptions import MCTuplesConstructionError
from .tuples import MC_TUPLES_SIZES, N_BINS, MCTuples


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
def generate_mc_tuples(t_total_sec: float, n_workers: int = 32, seed: int = 42) -> MCTuples:
    """Construct a nested Monte Carlo tuple set in about `t_total_sec` s; its first `k` tuples form size `k`.

    The construction runs 1 max-div solve per size in `MC_TUPLES_SIZES`, and splits `t_total_sec`
    over them as `MCTuplesConstructionSettings.from_total_time` describes:

    - from 60 s up, the construction uses the full population of candidates and all `n_workers` workers;
    - below 60 s, the construction uses fewer of both, for short runs such as tests.

    The total covers only the solves: drawing the population and checking each size take extra
    time.

    A rerun gives a set of equivalent quality, not the same set, because max-div's parallel solver
    runs on a wall-clock budget.

    Args:
        t_total_sec: The total wall-clock time of the solves, at least 1 s.
        n_workers: The number of max-div workers per solve when `t_total_sec` is 60 s or more; more workers search from
            more seeds, and may exceed the number of cores.
        seed: The seed of the population and of every solve.

    Raises:
        ValueError: If `t_total_sec` is below 1 s, or `n_workers` below 1.
        MCTuplesConstructionError: If a size breaks its bin or inclusion constraints, which can
            happen when `t_total_sec` is too short for max-div to meet them.
    """
    # Imported here, not at module level: importing max-div compiles its numba functions, which takes
    # minutes on a fresh install, and only a construction needs them.
    from .max_div_selection import select_tuples

    settings = MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers)
    population = _draw_population(settings.population_size, seed)
    # `prefix_indices` holds population indices in prefix order: each size's new tuples follow those
    # of the size below it, so the first `k` indices form size `k`.
    prefix_indices = np.empty(0, dtype=np.int64)
    for k in MC_TUPLES_SIZES:
        selection = select_tuples(
            population, k, prefix_indices, settings.t_budget_per_size_sec[k], settings.n_workers, seed
        )
        _check_selection(population, k, prefix_indices, selection)
        prefix_indices = np.concatenate([prefix_indices, np.setdiff1d(selection, prefix_indices)])
    return _tuples_at(population, prefix_indices)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _draw_population(population_size: int, seed: int) -> np.ndarray:
    """Return `population_size` uniform random tuples in the open unit square, as an `(n, 2)` float64 array.

    The full population is always drawn, and a smaller one is its prefix, so the candidates do not
    depend on the population size beyond how many are kept.
    """
    points = np.random.default_rng(seed).random((FULL_POPULATION_SIZE, 2))
    # `random` draws from [0, 1): a row with an exact 0 is dropped, so every kept row lies in the open unit square.
    points = points[(points > 0).all(axis=1)]
    return points[:population_size]


def _check_selection(population: np.ndarray, k: int, required_indices: np.ndarray, selection: np.ndarray) -> None:
    """Check that `selection` has `k` distinct tuples, includes `required_indices`, and balances its bins.

    Balanced bins hold `k / N_BINS ± 1` tuples each, on both axes.

    max-div treats constraints as soft and returns its least-violating selection, so a total time
    too short for the solver to meet them raises here, because the returned set would otherwise break
    them silently.

    Raises:
        MCTuplesConstructionError: If any check fails.
    """
    if np.unique(selection).size != k:
        raise MCTuplesConstructionError(f"Size {k}: max-div selected {np.unique(selection).size} distinct tuples.")
    n_missing = np.setdiff1d(required_indices, selection).size
    if n_missing > 0:
        raise MCTuplesConstructionError(f"Size {k}: {n_missing} tuples of the size below it are not selected.")
    stats = _tuples_at(population, selection).stats()
    if stats.max_bin_count_deviation > 1:
        raise MCTuplesConstructionError(
            f"Size {k}: the bin counts are {list(stats.bin_counts_u)} along u and {list(stats.bin_counts_v)} "
            f"along v, not all within 1 of {k // N_BINS}."
        )


def _tuples_at(population: np.ndarray, indices: np.ndarray) -> MCTuples:
    """Return the tuples of `population` at `indices`, in that order."""
    return MCTuples(population[indices, 0], population[indices, 1])
