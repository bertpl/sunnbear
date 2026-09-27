"""`generate_uv_tuples` constructs a nested set of (u, v) tuples, spread as evenly as max-div can make it.

The construction selects each size with max-div from a uniform random population of candidate tuples:

- **objective**: maximize the geometric mean of 3 min separations, each the smallest distance
  between 2 selected tuples: in the square (L2), along u and along v;
- **inclusion**: the sizes are built bottom-up, the smallest first, and each larger size is
  constrained to include the size below it, so every size is a prefix of the next;
- **spans**: span constraints cut each axis into `N_SPANS` equal spans, and keep each span's count
  of a size's tuples within 1 of `size / N_SPANS`.
"""

import warnings

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric
from max_div.solver import ParallelMaxDivSolverBuilder, ParallelSolvingWarning, Verbosity, seconds

from .construction_settings import FULL_POPULATION_SIZE, UvTuplesConstructionSettings
from .exceptions import UvTuplesConstructionError
from .tuples import N_SPANS, UV_TUPLES_SIZES, UvTuples, span_indices

# The inclusion constraint weighs more than the span constraints, so max-div meets it first.
INCLUSION_CONSTRAINT_WEIGHT = 10.0


# ==================================================================================================
#  generate_uv_tuples
# ==================================================================================================
def generate_uv_tuples(t_total_sec: float, n_workers: int = 32, seed: int = 42) -> UvTuples:
    """Construct a nested set of 1024 (u, v) tuples in about `t_total_sec` s; its first `k` rows form size `k`.

    The construction runs 1 max-div solve per size in `UV_TUPLES_SIZES`, and splits `t_total_sec`
    over them as `UvTuplesConstructionSettings.from_total_time` describes:

    - from 60 s up, it uses the full population of candidates and all `n_workers` workers;
    - below 60 s, it uses fewer of both, for short runs such as tests.

    The total covers only the solves: drawing the population and checking each size take extra
    time.

    A rerun gives a set of equivalent quality, not the same set, because max-div's parallel solver
    runs on a wall-clock budget.

    Args:
        t_total_sec: The total wall-clock time of the solves, at least 1 s.
        n_workers: The number of max-div workers per solve from 60 s up; more workers search from
            more seeds, and may exceed the number of cores.
        seed: The seed of the population and of every solve.

    Raises:
        ValueError: If `t_total_sec` is below 1 s, or `n_workers` below 1.
        UvTuplesConstructionError: If a size breaks its span or inclusion constraints, which can
            happen when `t_total_sec` is too short for max-div to meet them.
    """
    settings = UvTuplesConstructionSettings.from_total_time(t_total_sec, n_workers)
    population = _draw_population(settings.population_size, seed)
    # `prefix_indices` holds population indices in prefix order: each size's new tuples follow those
    # of the size below it, so the first `k` indices form size `k`.
    prefix_indices = np.empty(0, dtype=np.int64)
    for k in UV_TUPLES_SIZES:
        selection = _select_tuples(
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
    # `random` draws from [0, 1): a row with an exact 0 is dropped, which leaves the open square.
    points = points[(points > 0).all(axis=1)]
    return points[:population_size]


def _select_tuples(
    population: np.ndarray,
    k: int,
    required_indices: np.ndarray,
    t_budget_sec: float,
    n_workers: int,
    seed: int,
) -> np.ndarray:
    """Return max-div's selection of `k` tuples, including `required_indices`, as sorted population indices."""
    constraints = _span_constraints(population, k)
    if required_indices.size > 0:
        constraints.append(
            Constraint(
                int_set=set(required_indices.tolist()),
                min_count=required_indices.size,
                max_count=required_indices.size,
                weight=INCLUSION_CONSTRAINT_WEIGHT,
            )
        )
    problem = MaxDivProblem.new(
        # max-div ranks float32 copies; the selected tuples are taken from the float64 population by index.
        population.astype(np.float32),
        k=k,
        distance_metric=DistanceMetric.l2_euclidean(),
        diversity_metric=HybridDiversityMetric.geomean_of(
            DiversityMetric.MIN_SEPARATION.over(DistanceMetric.l2_euclidean()),
            DiversityMetric.MIN_SEPARATION.over(DistanceMetric.along_axis(0)),
            DiversityMetric.MIN_SEPARATION.over(DistanceMetric.along_axis(1)),
        ),
        constraints=constraints,
    )
    with warnings.catch_warnings():
        # max-div warns when a short run scales down to 1 worker, and when the workers outnumber the
        # cores; both are deliberate here (the second searches from more seeds).
        warnings.simplefilter("ignore", ParallelSolvingWarning)
        solver = (
            ParallelMaxDivSolverBuilder(problem)
            .with_seed(seed)
            .with_workers(seconds(t_budget_sec), n_workers)
            .with_end_to_end_budget()
            .build()
        )
    solution = solver.solve(verbosity=Verbosity.SILENT)
    return np.sort(np.asarray(solution.i_selected, dtype=np.int64))


def _span_constraints(population: np.ndarray, k: int) -> list[Constraint]:
    """Return 1 constraint per span of each axis, each allowing `k / N_SPANS ± 1` selected tuples."""
    per_span = k // N_SPANS
    constraints = []
    for axis in range(2):
        indices = span_indices(population[:, axis])
        for span in range(N_SPANS):
            constraints.append(
                Constraint(
                    int_set=set(np.flatnonzero(indices == span).tolist()),
                    min_count=per_span - 1,
                    max_count=per_span + 1,
                )
            )
    return constraints


def _check_selection(population: np.ndarray, k: int, required_indices: np.ndarray, selection: np.ndarray) -> None:
    """Check that `selection` has `k` distinct tuples, includes `required_indices`, and balances its spans.

    Balanced spans hold `k / N_SPANS ± 1` tuples each, on both axes.

    max-div treats constraints as soft and returns its least-violating selection, so a total time
    too short for the solver to meet them raises here, not in a returned set.

    Raises:
        UvTuplesConstructionError: If any check fails.
    """
    if np.unique(selection).size != k:
        raise UvTuplesConstructionError(f"Size {k}: max-div selected {np.unique(selection).size} distinct tuples.")
    n_missing = np.setdiff1d(required_indices, selection).size
    if n_missing > 0:
        raise UvTuplesConstructionError(f"Size {k}: {n_missing} tuples of the size below it are not selected.")
    stats = _tuples_at(population, selection).stats()
    if stats.max_span_count_deviation > 1:
        raise UvTuplesConstructionError(
            f"Size {k}: the span counts are {list(stats.span_counts_u)} along u and {list(stats.span_counts_v)} "
            f"along v, not all within 1 of {k // N_SPANS}."
        )


def _tuples_at(population: np.ndarray, indices: np.ndarray) -> UvTuples:
    """Return the tuples of `population` at `indices`, in that order."""
    return UvTuples(population[indices, 0], population[indices, 1])
