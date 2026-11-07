"""`select_diverse_problem_ids` selects diverse candidates from a `CandidatePool` by max-div, under tier quotas."""

import numba
import numpy as np
from max_div import Constraint, MaxDivProblem, ParallelMaxDivSolverBuilder, Verbosity, seconds
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric

from sunnbear._core.problems.core import ProblemId

from .candidate_pool import CandidatePool
from .difficulty_tier import DifficultyTier
from .difficulty_tier_quotas import DifficultyTierQuotas

# Each max-div worker runs for this many seconds of wall-clock time per candidate of the `CandidatePool`, so that the
# search time grows with the number of candidates to select from.
DEFAULT_SELECTION_SEC_PER_CANDIDATE = 0.2


# ==================================================================================================
#  select_diverse_problem_ids
# ==================================================================================================
def select_diverse_problem_ids(
    candidate_pool: CandidatePool,
    *,
    tier_quotas: DifficultyTierQuotas,
    seed: int,
    sec_per_candidate: float,
    n_workers: int,
) -> tuple[tuple[ProblemId, ...], float]:
    """Return the ids of max-div's most diverse selection of `tier_quotas.size` candidates, and its diversity score.

    max-div searches for the candidates whose scaled feature vectors from full characterization are the most diverse,
    under 1 constraint per quota of `tier_quotas`; a quota whose group holds every tier is no constraint.

    Its objective is the geometric mean, with equal weights, of the geometric mean separation under each of 2
    distances, where a selected candidate's separation is its distance to the nearest other selected candidate:

    - the L1 distance between the scaled feature vectors, in which every feature block has a mean pairwise L1 distance
      of 1;
    - the distance between the log2 of the EDIs, so that 2 EDIs compare by their ratio, and the selection's EDIs also
      differ widely within each quota.

    max-div receives each candidate's feature vector with 1 more column, the log2 of its EDI; the first distance,
    `l1_distance_over_leading_columns`, leaves that column out.

    The geometric mean weighs every selected candidate's separation equally. A statistic that weighs the smallest
    separations more would let the difficulty tiers whose candidates lie closest together decide the selection.

    Args:
        candidate_pool: The candidates to select from.
        tier_quotas: The quotas of the selection, whose sum is its size.
        seed: The seed of max-div's search.
        sec_per_candidate: The wall-clock time of max-div's search per candidate of `candidate_pool`. max-div searches
            with `n_workers` workers, in groups that share their best selections and merge as the search runs, so the
            selection depends on the timing of the workers and can differ between 2 calls.
        n_workers: The number of max-div's worker processes.

    Returns:
        The ids of the selected candidates, in the order of `candidate_pool`, and the diversity score of the selection.

    Raises:
        PipelineStopError: If the selection misses its size or a quota, as `DifficultyTierQuotas.check_selection`
            describes, because max-div treats its constraints as soft and returns its best selection even when it
            breaks one.
    """
    n_features = candidate_pool.feature_matrix.values.shape[1]
    feature_distance = DistanceMetric.custom(
        l1_distance_over_leading_columns, label="l1_over_features", params=(n_features,)
    )
    max_div_problem = MaxDivProblem.new(
        # max-div takes float32 vectors; the lost precision does not affect the output, which holds the selected
        # candidates, not their vectors.
        np.hstack([candidate_pool.feature_matrix.values, np.log2(candidate_pool.edis)[:, np.newaxis]]),
        k=tier_quotas.size,
        distance_metric=feature_distance,
        diversity_metric=HybridDiversityMetric.geomean_of(
            DiversityMetric.geomean_separation().over(feature_distance),
            DiversityMetric.geomean_separation().over(DistanceMetric.along_axis(n_features)),
        ),
        constraints=[
            Constraint(
                int_set={idx for idx, tier in enumerate(candidate_pool.difficulty_tiers) if tier in tiers},
                min_count=count,
                max_count=count,
            )
            for tiers, count in tier_quotas.counts.items()
            if len(tiers) < len(DifficultyTier)
        ],
    )
    solution = (
        ParallelMaxDivSolverBuilder(max_div_problem)
        .with_seed(seed)
        .with_workers(seconds(len(candidate_pool.feature_matrix.problem_ids) * sec_per_candidate), n_workers=n_workers)
        .build()
        .solve(verbosity=Verbosity.SILENT)
    )
    tier_quotas.check_selection([candidate_pool.difficulty_tiers[idx] for idx in solution.i_selected])
    selected_problem_ids = tuple(candidate_pool.feature_matrix.problem_ids[idx] for idx in sorted(solution.i_selected))
    return selected_problem_ids, solution.score.diversity


# ==================================================================================================
#  Helpers
# ==================================================================================================
# This function is module-level, because max-div's custom distance takes a `numba.njit` function and numba compiles
# no method.
@numba.njit(fastmath={"reassoc", "contract"})
def l1_distance_over_leading_columns(a: np.ndarray, b: np.ndarray, n_columns: int) -> float:
    """Return the L1 distance between the vectors `a` and `b` over their first `n_columns` coordinates."""
    distance = 0.0
    for idx in range(n_columns):
        distance += abs(a[idx] - b[idx])
    return distance
