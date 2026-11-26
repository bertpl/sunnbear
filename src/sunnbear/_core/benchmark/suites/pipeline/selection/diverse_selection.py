"""This module selects diverse candidates from a `CandidatePool` by max-div, and scores the diversity of candidates.

`select_diverse_problem_ids` searches for the most diverse selection under tier quotas, and `compute_diversity_score`
scores a given set of candidates. Both use 1 objective, which `_build_max_div_problem` defines: the geometric mean,
with equal weights, of the geometric mean separation under each of 2 distances, where a selected candidate's
separation is its distance to the nearest other selected candidate:

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
from .difficulty_tier_assignment import DifficultyTierAssignment
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
    quotas: DifficultyTierQuotas,
    required_problem_ids: Collection[ProblemId] = (),
    seed: int,
    sec_per_candidate: float,
    n_workers: int,
) -> tuple[tuple[ProblemId, ...], DifficultyTierAssignment]:
    """Return the most diverse selection that holds `required_problem_ids` and meets `quotas`, and the pool's tiers.

    `DifficultyTierAssignment.from_pool` assigns a tier to each candidate of `candidate_pool` that is not required.
    max-div searches, by the objective of this module, for a selection of the required candidates plus
    `quotas.selection_size` other candidates, under these constraints:

    - 1 per tier: the selection holds exactly the tier's quota of the candidates with that assigned tier;
    - 1 more when there are required candidates: the selection holds all of them, so the quotas count only the
      candidates that are not required.

    Args:
        candidate_pool: The candidates to select from.
        quotas: The quotas of the selection beyond the required candidates.
        required_problem_ids: The candidates of `candidate_pool` that must be in the selection.
        seed: The seed of max-div's search.
        sec_per_candidate: The wall-clock time of max-div's search per candidate of `candidate_pool`. max-div searches
            with `n_workers` workers, in groups that share their best selections and merge as the search runs, so the
            selection depends on the timing of the workers and can differ between 2 calls.
        n_workers: The number of max-div's worker processes.

    Returns:
        The ids of the selected candidates, the required ones included, in the order of `candidate_pool`, and the tier
        assignment of the candidates of `candidate_pool` that are not required.

    Raises:
        ValueError: If `candidate_pool` holds fewer than `quotas.selection_size` candidates that are not required, as
            `DifficultyTierAssignment.from_pool` describes.
        PipelineStopError: If the selection misses a required candidate, or misses a quota, as
            `DifficultyTierQuotas.check_selection` describes, because max-div treats its constraints as soft and
            returns its best selection even when it breaks one.
    """
    problem_ids = candidate_pool.feature_matrix.problem_ids
    required_problem_id_set = set(required_problem_ids)
    tier_assignment = DifficultyTierAssignment.from_pool(
        candidate_pool.subset([problem_id for problem_id in problem_ids if problem_id not in required_problem_id_set]),
        quotas,
    )

    # --- constraints ----------------------------
    # A required candidate has no assigned tier, so no tier's constraint counts it.
    assigned_tiers = [tier_assignment.assigned_tiers.get(problem_id) for problem_id in problem_ids]
    constraints = [
        Constraint(
            int_set={idx for idx, assigned_tier in enumerate(assigned_tiers) if assigned_tier is tier},
            min_count=quota,
            max_count=quota,
        )
        for tier, quota in quotas.quota_by_tier.items()
    ]
    if required_problem_id_set:
        constraints.append(
            Constraint(
                int_set={idx for idx, problem_id in enumerate(problem_ids) if problem_id in required_problem_id_set},
                min_count=len(required_problem_id_set),
                max_count=len(required_problem_id_set),
            )
        )

    # --- search ---------------------------------
    max_div_problem = _build_max_div_problem(
        candidate_pool, k=len(required_problem_id_set) + quotas.selection_size, constraints=constraints
    )
    solution = (
        ParallelMaxDivSolverBuilder(max_div_problem)
        .with_seed(seed)
        .with_workers(seconds(len(problem_ids) * sec_per_candidate), n_workers=n_workers)
        .build()
        .solve(verbosity=Verbosity.SILENT)
    )

    # --- checks ---------------------------------
    selected_indices = sorted(solution.i_selected)
    n_missing_required_candidates = len(required_problem_id_set - {problem_ids[idx] for idx in selected_indices})
    if n_missing_required_candidates:
        raise PipelineStopError(
            f"The selection misses {n_missing_required_candidates} of the {len(required_problem_id_set)} required "
            "candidates."
        )
    quotas.check_selection([assigned_tiers[idx] for idx in selected_indices if assigned_tiers[idx] is not None])
    return tuple(problem_ids[idx] for idx in selected_indices), tier_assignment


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
