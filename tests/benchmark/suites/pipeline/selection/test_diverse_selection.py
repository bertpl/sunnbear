"""These tests check the diverse selection of `CandidatePool` candidates by max-div:

- `select_diverse_problem_ids` records a quota that max-div's selection misses, and stops the pipeline when the
  selection misses a required candidate;
- with required candidates, its selection holds all of them, and the others meet the quotas;
- when a group holds fewer candidates than its quota, max-div returns a full selection that comes closest to the quotas;
- `select_diverse_problem_ids` refuses a pool too small for the selection;
- `compute_diversity_score` gives the geometric mean of the candidates' separations under both distances;
- the distance over the feature columns is the L1 distance that leaves the EDI column out.
"""

from fractions import Fraction
from types import SimpleNamespace

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTier,
    DifficultyTierCandidateGroup,
    QuotaFulfillment,
    ShareQuota,
    compute_diversity_score,
    select_diverse_problem_ids,
)
from sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection import l1_distance_over_leading_columns
from sunnbear._core.stats import l1_distances_to
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

_DIFFICULTY_TIER_QUOTAS = tuple(
    ShareQuota.exactly(DifficultyTierCandidateGroup(tiers=(tier,)), Fraction(1, 4)) for tier in DifficultyTier
)


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


def test_a_selection_that_misses_a_quota_records_the_miss(monkeypatch):
    """A stand-in for max-div's solver selects the first 16 of 28 candidates, all of tier A, so the fulfillments record
    16 candidates of A and none of the other tiers; no candidate is of tier D, so its quota has no constraint.

    max-div itself returns a selection that meets every quota that can be met, so only a stand-in returns this one.
    """
    # --- arrange ----------------------
    monkeypatch.setattr(
        "sunnbear._core.benchmark.suites.pipeline.selection.diverse_selection.ParallelMaxDivSolverBuilder",
        _FirstCandidatesSolverBuilder,
    )
    pool = _example_pool([5.0] * 16 + [15.0] * 6 + [30.0] * 6, seed=5)

    # --- act --------------------------
    selected_problem_ids, quota_fulfillments = select_diverse_problem_ids(
        pool, selection_size=16, quotas=_DIFFICULTY_TIER_QUOTAS, seed=1, sec_per_candidate=0.05, n_workers=2
    )

    # --- assert -----------------------
    assert selected_problem_ids == pool.feature_matrix.problem_ids[:16]
    assert quota_fulfillments == tuple(
        QuotaFulfillment(group_label=label, min_count=4, max_count=4, n_selected_in_group=n_selected_in_group)
        for label, n_selected_in_group in (("A", 16), ("B", 0), ("C", 0), ("D", 0))
    )


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

    # --- act / assert -----------------
    with pytest.raises(PipelineStopError, match=r"^The selection misses 8 of the 8 required candidates\.$"):
        select_diverse_problem_ids(
            pool,
            selection_size=16,
            quotas=_DIFFICULTY_TIER_QUOTAS,
            required_problem_ids=required_problem_ids,
            seed=1,
            sec_per_candidate=0.05,
            n_workers=2,
        )


@pytest.mark.only_with_numba_jit
def test_a_selection_with_required_candidates_holds_them_and_meets_the_quotas_over_the_others():
    """Of 64 candidates, 16 are required and the other 48 hold 12 of each tier; max-div's selection holds the 16
    required candidates and 4 of each tier of the others, so every quota is met."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed=7)
    edis = [*rng.uniform(4.0, 80.0, size=16), *(edi for edi in (5.0, 15.0, 30.0, 60.0) for _ in range(12))]
    pool = _example_pool(edis, seed=8)
    required_problem_ids = pool.feature_matrix.problem_ids[:16]

    # --- act --------------------------
    selected_problem_ids, quota_fulfillments = select_diverse_problem_ids(
        pool,
        selection_size=16,
        quotas=_DIFFICULTY_TIER_QUOTAS,
        required_problem_ids=required_problem_ids,
        seed=1,
        sec_per_candidate=0.05,
        n_workers=2,
    )

    # --- assert -----------------------
    assert len(selected_problem_ids) == 32
    assert set(required_problem_ids) <= set(selected_problem_ids)
    assert quota_fulfillments == tuple(
        QuotaFulfillment(group_label=tier.value, min_count=4, max_count=4, n_selected_in_group=4)
        for tier in DifficultyTier
    )


@pytest.mark.only_with_numba_jit
def test_a_group_with_too_few_candidates_misses_its_quota_and_the_selection_stays_full():
    """Only 3 of 39 candidates are of tier D, under a quota of 4 in a selection of 16; max-div selects all 3 of them,
    and fills the other 13 places from the other tiers, each with at least its quota of 4."""
    # --- arrange ----------------------
    pool = _example_pool([5.0] * 12 + [15.0] * 12 + [30.0] * 12 + [60.0] * 3, seed=9)

    # --- act --------------------------
    selected_problem_ids, quota_fulfillments = select_diverse_problem_ids(
        pool, selection_size=16, quotas=_DIFFICULTY_TIER_QUOTAS, seed=1, sec_per_candidate=0.05, n_workers=2
    )

    # --- assert -----------------------
    n_selected_by_label = {f.group_label: f.n_selected_in_group for f in quota_fulfillments}
    assert len(selected_problem_ids) == 16
    assert n_selected_by_label["D"] == 3
    assert all(n_selected_by_label[label] >= 4 for label in "ABC")
    assert sum(n_selected_by_label.values()) == 16


def test_a_pool_too_small_for_the_selection_is_refused():
    """A pool of 20 candidates, 8 of them required, leaves 12 for a selection of 16, and `select_diverse_problem_ids`
    refuses it."""
    # --- arrange ----------------------
    pool = _example_pool([5.0] * 20, seed=5)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"^A pool of 12 candidates that are not required cannot fill a selection"):
        select_diverse_problem_ids(
            pool,
            selection_size=16,
            quotas=(),
            required_problem_ids=pool.feature_matrix.problem_ids[:8],
            seed=1,
            sec_per_candidate=0.05,
            n_workers=2,
        )


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
