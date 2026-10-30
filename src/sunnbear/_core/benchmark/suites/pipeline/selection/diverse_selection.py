"""`select_diverse_suite` selects the most diverse suite of a `SuiteComposition` from a `CandidatePool` by max-div."""

from max_div import Constraint, MaxDivProblem, MaxDivSolution, ParallelMaxDivSolverBuilder, Verbosity, seconds
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric

from .candidate_pool import CandidatePool
from .suite_composition import SuiteComposition

# Each max-div worker runs for this many seconds of wall-clock time per candidate of the pool, so that the search time
# grows with the number of candidates to select from.
DEFAULT_SELECTION_SEC_PER_CANDIDATE = 0.2


# ==================================================================================================
#  select_diverse_suite
# ==================================================================================================
def select_diverse_suite(
    pool: CandidatePool,
    *,
    composition: SuiteComposition,
    seed: int,
    sec_per_candidate: float,
    n_workers: int,
) -> MaxDivSolution:
    """Return max-div's selection of the most diverse suite of `composition` from `pool`.

    max-div searches for the `composition.size` candidates whose scaled full feature vectors are the most diverse,
    under 1 constraint per quota of `composition`.

    Its objective is the geometric mean, with equal weights, of the geometric mean separation under each of 2
    distances, where a selected candidate's separation is its distance to the nearest other selected candidate:

    - the L1 distance between the scaled vectors, in which every feature block has a mean pairwise L1 distance of 1;
    - the distance along the EDI feature, which is the EDI on a log scale, so that the suite's EDIs also differ widely
      within each quota.

    The distance along the EDI feature therefore compares 2 EDIs by their ratio. `map_fevals_to_feature` and the scale
    of the solvers block multiply that distance by a constant factor, which does not change which selection maximizes
    a geometric mean.

    The geometric mean weighs every selected candidate's separation equally. A statistic that weighs the smallest
    separations more would let the difficulty classes whose candidates lie closest together steer the selection.

    Args:
        pool: The candidates to select from.
        composition: The quotas of the suite to select.
        seed: The seed of max-div's search.
        sec_per_candidate: The wall-clock time of max-div's search per candidate of `pool`. max-div searches with
            `n_workers` workers, in groups that share their best selections and merge as the search runs, so the
            selection depends on the timing of the workers and can differ between 2 calls.
        n_workers: The number of max-div's worker processes.

    Returns:
        max-div's solution, whose ``i_selected`` holds the selected rows of `pool`, ascending.

    Raises:
        PipelineStopError: If the selection misses the suite's size or a quota, as `SuiteComposition.check_selection`
            describes, because max-div treats its constraints as soft and returns its best selection even when it
            breaks one.
    """
    max_div_problem = MaxDivProblem.new(
        # max-div takes float32 vectors; the lost precision does not reach the output, because a stage takes the
        # selected rows from its input table by index.
        pool.vectors,
        k=composition.size,
        distance_metric=DistanceMetric.l1_manhattan(),
        diversity_metric=HybridDiversityMetric.geomean_of(
            DiversityMetric.geomean_separation().over(DistanceMetric.l1_manhattan()),
            DiversityMetric.geomean_separation().over(DistanceMetric.along_axis(pool.edi_axis)),
        ),
        constraints=[
            Constraint(
                int_set={idx for idx, c in enumerate(pool.difficulty_classes) if c in quota.classes},
                min_count=quota.count,
                max_count=quota.count,
            )
            for quota in composition.quotas
        ],
    )
    solution = (
        ParallelMaxDivSolverBuilder(max_div_problem)
        .with_seed(seed)
        .with_workers(seconds(len(pool.vectors) * sec_per_candidate), n_workers=n_workers)
        .build()
        .solve(verbosity=Verbosity.SILENT)
    )
    composition.check_selection([pool.difficulty_classes[idx] for idx in solution.i_selected])
    return solution
