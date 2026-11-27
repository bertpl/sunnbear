"""This module selects diverse candidates from a `CandidatePool` by max-div, and scores the diversity of candidates.

`select_diverse_problem_ids` searches for the most diverse selection under quotas on groups of candidates, and
`compute_diversity_score` scores a given set of candidates.

Both use 1 objective, which `_build_max_div_problem` defines: the geometric mean, with equal weights, of the geometric
mean separation under each of 2 distances, where a selected candidate's separation is its distance to the nearest
other selected candidate:

- the L1 distance between the scaled feature vectors, in which every feature block has a mean pairwise L1 distance
  of 1;
- the distance between the log2 of the EDIs, so that 2 EDIs compare by their ratio; this distance makes the search
  spread the selected EDIs within each tier.

The geometric mean weighs every selected candidate's separation equally. A statistic that weighs the smallest
separations more would let the difficulty tiers whose candidates lie closest together decide the selection.
"""

from collections.abc import Collection, Sequence

import numba
import numpy as np
from max_div import (
    Constraint,
    MaxDivProblem,
    MaxDivSolverBuilder,
    ParallelMaxDivSolverBuilder,
    Verbosity,
    seconds,
)
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.problems.core import ProblemId

from .candidate_pool import CandidatePool
from .quota_fulfillment import QuotaFulfillment
from .share_quota import ShareQuota

# Each max-div worker runs for this many seconds of wall-clock time per candidate of the `CandidatePool`, so that the
# search time grows with the number of candidates to select from.
DEFAULT_SELECTION_SEC_PER_CANDIDATE = 0.2


# ==================================================================================================
#  select_diverse_problem_ids
# ==================================================================================================
def select_diverse_problem_ids(
    candidate_pool: CandidatePool,
    *,
    selection_size: int,
    quotas: Sequence[ShareQuota],
    required_problem_ids: Collection[ProblemId] = (),
    seed: int,
    sec_per_candidate: float,
    n_workers: int,
) -> tuple[tuple[ProblemId, ...], tuple[QuotaFulfillment, ...]]:
    """Return the most diverse selection with `required_problem_ids` that best meets `quotas`, and how it meets each.

    max-div searches, by the objective of this module, for a selection of the required candidates plus `selection_size`
    other candidates, under these constraints:

    - 1 per quota: the selection holds at least the quota's smallest count and at most its largest count of the
      candidates of the quota's group, with the counts that `ShareQuota.for_selection` gives for `selection_size`; a
      group holds only candidates that are not required;
    - 1 more when there are required candidates: the selection holds all of them.

    max-div meets every constraint that can be met. When the quotas cannot all be met, for example because a group
    holds fewer candidates than its quota's smallest count, max-div returns the selection that comes closest to them,
    and the returned fulfillments show each quota that the selection misses.

    Args:
        candidate_pool: The candidates to select from.
        selection_size: The number of selected candidates beyond the required ones; each quota's shares of it must be
            whole numbers of candidates.
        quotas: The quotas of the selection beyond the required candidates; empty for a selection without quotas.
        required_problem_ids: The candidates of `candidate_pool` that must be in the selection.
        seed: The seed of max-div's search.
        sec_per_candidate: The wall-clock time of max-div's search per candidate of `candidate_pool`. max-div searches
            with `n_workers` workers, in groups that share their best selections and merge as the search runs, so the
            selection depends on the timing of the workers and can differ between 2 calls.
        n_workers: The number of max-div's worker processes.

    Returns:
        The ids of the selected candidates, the required ones included, in the order of `candidate_pool`, and the
        `QuotaFulfillment` of each quota, in the order of `quotas`.

    Raises:
        ValueError: If `candidate_pool` holds fewer than `selection_size` candidates that are not required, or a share
            of a quota is not a whole number of candidates, as `ShareQuota.for_selection` describes.
        PipelineStopError: If the selection misses a required candidate.
    """
    problem_ids = candidate_pool.feature_matrix.problem_ids
    required_problem_id_set = set(required_problem_ids)
    non_required_pool = candidate_pool.subset(
        [problem_id for problem_id in problem_ids if problem_id not in required_problem_id_set]
    )
    n_non_required_candidates = len(non_required_pool.feature_matrix.problem_ids)
    if n_non_required_candidates < selection_size:
        raise ValueError(
            f"A pool of {n_non_required_candidates} candidates that are not required cannot fill a selection of "
            f"{selection_size}."
        )
    else:
        count_quotas = [quota.for_selection(non_required_pool, selection_size=selection_size) for quota in quotas]

        # --- constraints ------------------------
        row_index_by_problem_id = candidate_pool.feature_matrix.row_index_by_problem_id
        # A group without candidates has nothing to select and gets no constraint, because max-div refuses a
        # constraint on no candidates; its fulfillment still records whether the selection meets its quota.
        constraints = [
            count_quota.to_constraint(row_index_by_problem_id) for count_quota in count_quotas if count_quota.member_ids
        ]
        if required_problem_id_set:
            constraints.append(
                Constraint(
                    int_set={row_index_by_problem_id[problem_id] for problem_id in required_problem_id_set},
                    min_count=len(required_problem_id_set),
                    max_count=len(required_problem_id_set),
                )
            )

        # --- search -----------------------------
        max_div_problem = _build_max_div_problem(
            candidate_pool, k=len(required_problem_id_set) + selection_size, constraints=constraints
        )
        solution = (
            ParallelMaxDivSolverBuilder(max_div_problem)
            .with_seed(seed)
            .with_workers(seconds(len(problem_ids) * sec_per_candidate), n_workers=n_workers)
            .build()
            .solve(verbosity=Verbosity.SILENT)
        )

        # --- check and fulfillments -------------
        selected_problem_ids = tuple(problem_ids[idx] for idx in sorted(solution.i_selected))
        n_missing_required_candidates = len(required_problem_id_set - set(selected_problem_ids))
        if n_missing_required_candidates:
            raise PipelineStopError(
                f"The selection misses {n_missing_required_candidates} of the {len(required_problem_id_set)} required "
                "candidates."
            )
        else:
            return selected_problem_ids, tuple(
                count_quota.fulfillment(selected_problem_ids) for count_quota in count_quotas
            )


# ==================================================================================================
#  compute_diversity_score
# ==================================================================================================
def compute_diversity_score(candidate_pool: CandidatePool) -> float:
    """Return the diversity score of all candidates of `candidate_pool`, by the objective of this module.

    max-div scores the selection that holds all candidates without searching, so the score equals the score that
    `select_diverse_problem_ids`'s search assigns to a selection of exactly these candidates.
    """
    n_candidates = len(candidate_pool.feature_matrix.problem_ids)
    max_div_problem = _build_max_div_problem(candidate_pool, k=n_candidates, constraints=())
    solution = (
        MaxDivSolverBuilder(max_div_problem)
        .with_initial_selection(np.arange(n_candidates))
        .build()
        .solve(verbosity=Verbosity.SILENT)
    )
    return float(solution.score.diversity)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _build_max_div_problem(
    candidate_pool: CandidatePool, *, k: int, constraints: Sequence[Constraint]
) -> MaxDivProblem:
    """Return the max-div problem of selecting `k` candidates of `candidate_pool` under `constraints`.

    The problem holds the objective of this module. max-div receives each candidate's feature vector with 1 more
    column, the log2 of its EDI; the distance over the features, `l1_distance_over_leading_columns`, leaves that column
    out.
    """
    n_features = candidate_pool.feature_matrix.values.shape[1]
    feature_distance = DistanceMetric.custom(
        l1_distance_over_leading_columns, label="l1_over_features", params=(n_features,)
    )
    return MaxDivProblem.new(
        # max-div takes float32 vectors; the lost precision does not affect the output, which holds the selected
        # candidates, not their vectors.
        np.hstack([candidate_pool.feature_matrix.values, np.log2(candidate_pool.edis)[:, np.newaxis]]),
        k=k,
        distance_metric=feature_distance,
        diversity_metric=HybridDiversityMetric.geomean_of(
            DiversityMetric.geomean_separation().over(feature_distance),
            DiversityMetric.geomean_separation().over(DistanceMetric.along_axis(n_features)),
        ),
        constraints=list(constraints),
    )


# This function is module-level, because max-div's custom distance takes a `numba.njit` function and numba compiles
# no method.
@numba.njit(fastmath={"reassoc", "contract"})
def l1_distance_over_leading_columns(a: np.ndarray, b: np.ndarray, n_columns: int) -> float:
    """Return the L1 distance between the vectors `a` and `b` over their first `n_columns` coordinates."""
    distance = 0.0
    for idx in range(n_columns):
        distance += abs(a[idx] - b[idx])
    return distance
