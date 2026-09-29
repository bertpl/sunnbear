"""`select_tuples` runs the max-div solver once, to select the tuples of 1 size of the tuple set from the population."""

import warnings

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric
from max_div.solver import ParallelMaxDivSolverBuilder, ParallelSolvingWarning, Verbosity, seconds

from .exceptions import MCTuplesConstructionError
from .tuples import N_BINS, MCTuples, axis_bin_indices

# The inclusion constraint weighs more than the bin constraints, so max-div meets it first.
INCLUSION_CONSTRAINT_WEIGHT = 10.0


# ==================================================================================================
#  select_tuples
# ==================================================================================================
def select_tuples(
    population: np.ndarray,
    k: int,
    required_indices: np.ndarray,
    t_budget_sec: float,
    n_workers: int,
    seed: int,
) -> np.ndarray:
    """Return max-div's selection of `k` tuples, including `required_indices`, as sorted population indices.

    max-div weighs the bin and inclusion constraints against the objective without enforcing them, so the
    selection is checked against them before it is returned.

    Raises:
        MCTuplesConstructionError: If the selection breaks its bin or inclusion constraints, which can
            happen when `t_budget_sec` is too short for max-div to meet them.
    """
    constraints = _bin_constraints(population, k)
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
        # max-div works on a float32 copy; the selected tuples are taken from the float64 population by index.
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
    selection = np.sort(np.asarray(solution.i_selected, dtype=np.int64))
    _check_selection(population, k, required_indices, selection)
    return selection


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _bin_constraints(population: np.ndarray, k: int) -> list[Constraint]:
    """Return 1 constraint per bin of each axis, each allowing `k / N_BINS ± 1` selected tuples."""
    target_count_per_bin = k // N_BINS
    constraints = []
    for axis in range(2):
        indices = axis_bin_indices(population[:, axis])
        for bin_index in range(N_BINS):
            constraints.append(
                Constraint(
                    int_set=set(np.flatnonzero(indices == bin_index).tolist()),
                    min_count=target_count_per_bin - 1,
                    max_count=target_count_per_bin + 1,
                )
            )
    return constraints


def _check_selection(population: np.ndarray, k: int, required_indices: np.ndarray, selection: np.ndarray) -> None:
    """Check that `selection` has `k` distinct tuples, includes `required_indices`, and balances its bins.

    Balanced bins hold `k / N_BINS ± 1` tuples each, on both axes.

    Raises:
        MCTuplesConstructionError: If any check fails.
    """
    if np.unique(selection).size != k:
        raise MCTuplesConstructionError(f"Size {k}: max-div selected {np.unique(selection).size} distinct tuples.")
    n_missing = np.setdiff1d(required_indices, selection).size
    if n_missing > 0:
        raise MCTuplesConstructionError(f"Size {k}: {n_missing} tuples of the size below it are not selected.")
    stats = MCTuples.from_population(population, selection).stats()
    if stats.max_bin_count_deviation > 1:
        raise MCTuplesConstructionError(
            f"Size {k}: the bin counts are {list(stats.bin_counts_u)} along u and {list(stats.bin_counts_v)} "
            f"along v, not all within 1 of {k // N_BINS}."
        )
