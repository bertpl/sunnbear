"""The diverse selection of `CandidatePool` candidates by max-div:

- `select_diverse_problem_ids` stops the pipeline when max-div's selection misses a quota or a required candidate;
- it refuses a tier assignment that does not cover exactly the candidates that are not required;
- with required candidates, its selection holds all of them, and the others meet the quotas;
- `compute_diversity_score` gives the geometric mean of the candidates' separations under both distances;
- the distance over the feature columns is the L1 distance that leaves the EDI column out.
"""

from types import SimpleNamespace

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTierAssignment,
    DifficultyTierQuotas,
    compute_diversity_score,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection import l1_distance_over_leading_columns
from sunnbear._core.stats import l1_distances_to
from tests.benchmark.suites.pipeline.example_states import example_problem_ids


class _FirstCandidatesSolverBuilder:
    """`_FirstCandidatesSolverBuilder` stands in for max-div's solver builder, and selects the first k candidates."""

    def __init__(self, max_div_problem: object) -> None:
        """Keep the problem, whose `k` sets the number of candidates to select."""
        self.max_div_problem = max_div_problem

    def with_seed(self, seed: int) -> "_FirstCandidatesSolverBuilder":
        """Return the builder, which ignores the seed."""
        return self

    def with_workers(self, duration: object, n_workers: int) -> "_FirstCandidatesSolverBuilder":
        """Return the builder, which ignores the time and the workers."""
        return self

    def build(self) -> "_FirstCandidatesSolverBuilder":
        """Return the builder, which also acts as its solver."""
        return self

    def solve(self, verbosity: object) -> SimpleNamespace:
        """Return a solution that selects the first k candidates."""
        return SimpleNamespace(i_selected=list(range(self.max_div_problem.k)))


def _example_pool(edis: list[float], *, seed: int) -> CandidatePool:
    """Return a pool of 1 example candidate per EDI of `edis`, with random features in 4 columns."""
    rng = np.random.default_rng(seed=seed)
    return CandidatePool(
        feature_matrix=FeatureMatrix(
            problem_ids=tuple(example_problem_ids(len(edis))), values=rng.random((len(edis), 4))
        ),
        edis=np.array(edis),
        n_bisection_fevals=40,
    )


def test_a_selection_that_misses_a_quota_stops_the_pipeline(monkeypatch):
    """A stand-in for max-div's solver selects the first 16 of 32 candidates, all of tier A, so the check after the
    selection stops the pipeline.

    With 1 constraint per tier on disjoint sets, max-div itself refuses a constraint that it cannot meet, so only a
    stand-in reaches the check.
    """
    # --- arrange ----------------------
    monkeypatch.setattr(
        "sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection.ParallelMaxDivSolverBuilder",
        _FirstCandidatesSolverBuilder,
    )
    pool = _example_pool([5.0] * 16 + [15.0] * 4 + [30.0] * 4 + [60.0] * 4 + [120.0] * 4, seed=5)
    tier_assignment = DifficultyTierAssignment.from_pool(pool, DifficultyTierQuotas(16))

    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"unmet quotas: A: 16 of 4; B: 0 of 4; C: 0 of 4; D: 0 of 4\."):
        select_diverse_problem_ids(pool, tier_assignment=tier_assignment, seed=1, sec_per_candidate=0.05, n_workers=2)


def test_a_selection_that_misses_a_required_candidate_stops_the_pipeline(monkeypatch):
    """The last 8 of 32 candidates are required, and a stand-in for max-div's solver selects the first 24, so the check
    after the selection stops the pipeline, and the message counts the missed candidates."""
    # --- arrange ----------------------
    monkeypatch.setattr(
        "sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection.ParallelMaxDivSolverBuilder",
        _FirstCandidatesSolverBuilder,
    )
    pool = _example_pool([5.0] * 6 + [15.0] * 6 + [30.0] * 6 + [60.0] * 6 + [5.0] * 8, seed=5)
    required_problem_ids = pool.feature_matrix.problem_ids[24:]
    tier_assignment = DifficultyTierAssignment.from_pool(
        pool.subset(pool.feature_matrix.problem_ids[:24]), DifficultyTierQuotas(16)
    )

    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"^The selection misses 8 of the 8 required candidates\.$"):
        select_diverse_problem_ids(
            pool,
            tier_assignment=tier_assignment,
            required_problem_ids=required_problem_ids,
            seed=1,
            sec_per_candidate=0.05,
            n_workers=2,
        )


def test_the_tier_assignment_must_cover_exactly_the_candidates_that_are_not_required():
    """A tier assignment over all 32 candidates is refused when 8 of them are required."""
    # --- arrange ----------------------
    pool = _example_pool([5.0] * 8 + [15.0] * 8 + [30.0] * 8 + [60.0] * 8, seed=5)
    tier_assignment = DifficultyTierAssignment.from_pool(pool, DifficultyTierQuotas(16))

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="must cover exactly the candidates of the pool that are not required"):
        select_diverse_problem_ids(
            pool,
            tier_assignment=tier_assignment,
            required_problem_ids=pool.feature_matrix.problem_ids[:8],
            seed=1,
            sec_per_candidate=0.05,
            n_workers=2,
        )


@pytest.mark.only_with_numba_jit
def test_a_selection_with_required_candidates_holds_them_and_meets_the_quotas_over_the_others():
    """Of 64 candidates, 16 are required and the other 48 hold 12 of each tier; max-div's selection holds the 16
    required candidates and 4 of each tier of the others."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed=7)
    edis = [*rng.uniform(4.0, 80.0, size=16), *(edi for edi in (5.0, 15.0, 30.0, 60.0) for _ in range(12))]
    pool = _example_pool(edis, seed=8)
    required_problem_ids = pool.feature_matrix.problem_ids[:16]
    tier_assignment = DifficultyTierAssignment.from_pool(
        pool.subset(pool.feature_matrix.problem_ids[16:]), DifficultyTierQuotas(16)
    )

    # --- act --------------------------
    selected_problem_ids = select_diverse_problem_ids(
        pool,
        tier_assignment=tier_assignment,
        required_problem_ids=required_problem_ids,
        seed=1,
        sec_per_candidate=0.05,
        n_workers=2,
    )

    # --- assert -----------------------
    assert len(selected_problem_ids) == 32
    assert set(required_problem_ids) <= set(selected_problem_ids)
    other_tiers = [tier_assignment.assigned_tiers[p] for p in selected_problem_ids if p not in required_problem_ids]
    assert sorted(other_tiers) == sorted(tier for tier in tier_assignment.quotas.quota_by_tier for _ in range(4))


@pytest.mark.only_with_numba_jit
@pytest.mark.parametrize(
    "features, edis, diversity_expected",
    [
        # The separations are 1, 1 and 2 under both distances, so each geometric mean, and the score, is 2^(1/3).
        pytest.param([[0.0], [1.0], [3.0]], [1.0, 2.0, 8.0], 2 ** (1 / 3), id="separate"),
        # The last 2 candidates share their EDI, so their separation along the EDIs is 0, and so is the score.
        pytest.param([[0.0], [1.0], [3.0]], [1.0, 4.0, 4.0], 0.0, id="equal_edis"),
    ],
)
def test_the_diversity_score_is_the_geomean_of_the_separations_under_both_distances(features, edis, diversity_expected):
    """The score of 3 candidates is the geometric mean, over the feature distance and the distance between the log2 of
    the EDIs, of the geometric mean of the candidates' distances to their nearest other candidate."""
    # --- arrange ----------------------
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(example_problem_ids(3)), values=np.array(features)),
        edis=np.array(edis),
        n_bisection_fevals=40,
    )

    # --- act / assert -----------------
    assert compute_diversity_score(pool) == pytest.approx(diversity_expected, rel=1e-6)


def test_the_feature_distance_is_the_l1_distance_over_the_leading_columns():
    """Over the first 4 of 5 columns, the distance equals the L1 distance between the vectors without their last
    column."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed=6)
    a, b = rng.random(5).astype(np.float32), rng.random(5).astype(np.float32)

    # --- act --------------------------
    distance = l1_distance_over_leading_columns(a, b, 4)

    # --- assert -----------------------
    assert distance == pytest.approx(l1_distances_to(a[np.newaxis, :4], b[:4])[0], rel=1e-6)
