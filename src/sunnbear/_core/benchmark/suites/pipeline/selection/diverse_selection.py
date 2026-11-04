"""`select_diverse_suite` selects the most diverse suite of a `SuiteComposition` from a `CandidatePool` by max-div."""

from dataclasses import dataclass

import numba
import numpy as np
from max_div import Constraint, MaxDivProblem, ParallelMaxDivSolverBuilder, Verbosity, seconds
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric

from sunnbear._core.problems.core import ProblemId

from .candidate_pool import CandidatePool
from .suite_composition import SuiteComposition

# Each max-div worker runs for this many seconds of wall-clock time per candidate of the `CandidatePool`, so that the
# search time grows with the number of candidates to select from.
DEFAULT_SELECTION_SEC_PER_CANDIDATE = 0.2


# ==================================================================================================
#  select_diverse_suite
# ==================================================================================================
def select_diverse_suite(
    candidate_pool: CandidatePool,
    *,
    composition: SuiteComposition,
    seed: int,
    sec_per_candidate: float,
    n_workers: int,
) -> "DiverseSuite":
    """Return max-div's selection of the most diverse suite of `composition` from `candidate_pool`.

    max-div searches for the `composition.size` candidates whose scaled feature vectors from full characterization
    are the most diverse, under 1 constraint per quota of `composition`.

    Its objective is the geometric mean, with equal weights, of the geometric mean separation under each of 2
    distances, where a selected candidate's separation is its distance to the nearest other selected candidate:

    - the L1 distance between the scaled feature vectors, in which every feature block has a mean pairwise L1 distance
      of 1;
    - the distance between the log2 of the EDIs, so that 2 EDIs compare by their ratio, and the suite's EDIs also
      differ widely within each quota.

    max-div receives each candidate's feature vector with 1 more column, the log2 of its EDI; the first distance,
    `l1_distance_over_leading_columns`, leaves that column out.

    The geometric mean weighs every selected candidate's separation equally. A statistic that weighs the smallest
    separations more would let the difficulty classes whose candidates lie closest together decide the selection.

    Args:
        candidate_pool: The candidates to select from.
        composition: The quotas of the suite to select.
        seed: The seed of max-div's search.
        sec_per_candidate: The wall-clock time of max-div's search per candidate of `candidate_pool`. max-div searches
            with `n_workers` workers, in groups that share their best selections and merge as the search runs, so the
            selection depends on the timing of the workers and can differ between 2 calls.
        n_workers: The number of max-div's worker processes.

    Raises:
        PipelineStopError: If the selection misses the suite's size or a quota, as `SuiteComposition.check_selection`
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
        k=composition.size,
        distance_metric=feature_distance,
        diversity_metric=HybridDiversityMetric.geomean_of(
            DiversityMetric.geomean_separation().over(feature_distance),
            DiversityMetric.geomean_separation().over(DistanceMetric.along_axis(n_features)),
        ),
        constraints=[
            Constraint(
                int_set={idx for idx, c in enumerate(candidate_pool.difficulty_classes) if c in quota.classes},
                min_count=quota.count,
                max_count=quota.count,
            )
            for quota in composition.quotas
        ],
    )
    solution = (
        ParallelMaxDivSolverBuilder(max_div_problem)
        .with_seed(seed)
        .with_workers(seconds(len(candidate_pool.feature_matrix.problem_ids) * sec_per_candidate), n_workers=n_workers)
        .build()
        .solve(verbosity=Verbosity.SILENT)
    )
    composition.check_selection([candidate_pool.difficulty_classes[idx] for idx in solution.i_selected])
    return DiverseSuite(
        problem_ids=tuple(candidate_pool.feature_matrix.problem_ids[idx] for idx in sorted(solution.i_selected)),
        diversity=solution.score.diversity,
    )


# ==================================================================================================
#  DiverseSuite
# ==================================================================================================
@dataclass(frozen=True)
class DiverseSuite:
    """A `DiverseSuite` holds the candidates that `select_diverse_suite` selects, and the score of the selection.

    Attributes:
        problem_ids: The ids of the selected candidates, in the order of the `CandidatePool`.
        diversity: The diversity score of max-div's selection.
    """

    problem_ids: tuple[ProblemId, ...]
    diversity: float


# ==================================================================================================
#  Helpers
# ==================================================================================================
# A module-level function, because max-div's custom distance takes a `numba.njit` function and numba compiles no
# method.
@numba.njit(fastmath={"reassoc", "contract"})
def l1_distance_over_leading_columns(a: np.ndarray, b: np.ndarray, n_columns: int) -> float:
    """Return the L1 distance between the vectors `a` and `b` over their first `n_columns` coordinates."""
    distance = 0.0
    for idx in range(n_columns):
        distance += abs(a[idx] - b[idx])
    return distance
