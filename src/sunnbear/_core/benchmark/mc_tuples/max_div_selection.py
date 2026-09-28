"""`select_tuples` runs the max-div solver once, to select the tuples of 1 size of the tuple set from the population.

Import this module only inside the function that needs it: importing max-div compiles its numba
functions, which takes minutes on a fresh install.
"""

import warnings

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric
from max_div.solver import ParallelMaxDivSolverBuilder, ParallelSolvingWarning, Verbosity, seconds

from .tuples import N_BINS, axis_bin_indices

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
    selection can break them when `t_budget_sec` is too short; check it before use.
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
    return np.sort(np.asarray(solution.i_selected, dtype=np.int64))


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
