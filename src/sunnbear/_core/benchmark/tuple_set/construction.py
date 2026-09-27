"""`generate_uv_tuples` constructs a nested set of (u, v) tuples, spread as evenly as max-div can make it.

The construction selects each size from a uniform random population of candidate tuples with
max-div, maximizing the geometric mean of 3 min separations: in the square (L2), along u and along
v. It builds the sizes bottom-up: 32 first, then each larger size under a constraint that it
includes the size below it, so the result is nested and every size is a prefix of the next. Span
constraints keep every size's tuples within 1 of `size / 8` per eighth of each axis.

max-div's parallel solver runs on a wall-clock budget, so a rerun with the same arguments selects
another set of equivalent quality, not the same one.
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
    """Construct a nested set of 1024 (u, v) tuples in about `t_total_sec` seconds; its first `k` rows form each size `k`.

    The construction runs 1 max-div solve per size (32, 64, …, 1024), and splits `t_total_sec`
    over them as `UvTuplesConstructionSettings.from_total_time` describes: from 60 s up, the full
    population of 65,536 candidates and all `n_workers` workers; below 60 s, fewer of both, for
    short runs such as tests. The total is approximate: drawing the population and checking each
    size come on top.

    A rerun gives a set of equivalent quality, not the same set, because max-div's parallel solver
    runs on a wall-clock budget.

    Args:
        t_total_sec: The total wall-clock time of the solves, at least 1 s.
        n_workers: The number of max-div workers per solve from 60 s up; more workers search from
            more seeds, and may exceed the number of cores.
        seed: The seed of the population and of every solve.

    Raises:
        ValueError: If `t_total_sec` is below 1 s, or `n_workers` below 1.
        UvTuplesConstructionError: If a size breaks its span or inclusion constraints, which a
            total too short for max-div to meet them can cause.
    """
    settings = UvTuplesConstructionSettings.from_total_time(t_total_sec, n_workers)
    population = _draw_population(settings.population_size, seed)
    # Population indices in prefix order: each size's new tuples are appended after the size below it.
    selected = np.empty(0, dtype=np.int64)
    for k in UV_TUPLES_SIZES:
        selection = _select(population, k, selected, settings.t_budget_per_tier_sec[k], settings.n_workers, seed)
        _check_selection(population, k, selected, selection)
        selected = np.concatenate([selected, np.setdiff1d(selection, selected)])
    return UvTuples(population[selected, 0], population[selected, 1])


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


def _select(
    population: np.ndarray,
    k: int,
    must_include: np.ndarray,
    t_budget_sec: float,
    n_workers: int,
    seed: int,
) -> np.ndarray:
    """Return the population indices of `k` tuples that max-div selects, including `must_include`, sorted."""
    constraints = _span_constraints(population, k)
    if must_include.size > 0:
        constraints.append(
            Constraint(
                int_set=set(must_include.tolist()),
                min_count=must_include.size,
                max_count=must_include.size,
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


def _check_selection(population: np.ndarray, k: int, must_include: np.ndarray, selection: np.ndarray) -> None:
    """Check that `selection` holds `k` distinct tuples, includes `must_include`, and keeps every span within 1.

    Raises:
        UvTuplesConstructionError: If any check fails.
    """
    if np.unique(selection).size != k:
        raise UvTuplesConstructionError(f"Size {k}: max-div selected {np.unique(selection).size} distinct tuples.")
    n_missing = np.setdiff1d(must_include, selection).size
    if n_missing > 0:
        raise UvTuplesConstructionError(f"Size {k}: {n_missing} tuples of the size below it are not selected.")
    stats = UvTuples(population[selection, 0], population[selection, 1]).stats()
    if stats.max_span_count_deviation > 1:
        raise UvTuplesConstructionError(
            f"Size {k}: the span counts are {list(stats.span_counts_u)} along u and {list(stats.span_counts_v)} "
            f"along v, not all within 1 of {k // N_SPANS}."
        )
