"""`DifficultyTierAssignment.from_pool` moves the limits between the tiers' candidates, in the order of their EDIs,
until the pool meets every quota:

- a tier below its quota takes candidates from the nearest tier with a surplus, through the tiers in between;
- with surpluses equally near on both sides, the tier below its quota takes, of the 2 candidates just outside its
  own in EDI order, the one whose EDI is closer to its own range;
- among equal EDIs, the pool's order decides;
- `from_pool` refuses a pool smaller than the selection.
"""

from collections import Counter
from collections.abc import Sequence

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTier,
    DifficultyTierAssignment,
    DifficultyTierQuotas,
)
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

A, B, C, D = DifficultyTier

# With 40 bisection evaluations, the tiers' EDI ranges start at 0, 10, 20 and 40.
_N_BISECTION_FEVALS = 40


def _pool(edis: Sequence[float]) -> CandidatePool:
    """Return a pool of 1 example candidate per EDI of `edis`, in that order, with random features."""
    problem_ids = example_problem_ids(len(edis))
    rng = np.random.default_rng(seed=7)
    return CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(problem_ids), values=rng.random((len(edis), 3))),
        edis=np.array(edis, dtype=float),
        n_bisection_fevals=_N_BISECTION_FEVALS,
    )


def _edis_of_tiers(pool_tier_counts: dict[DifficultyTier, int]) -> list[float]:
    """Return EDIs with `pool_tier_counts` of each tier, spread inside each tier's range, in a shuffled order."""
    edis = []
    for tier, count in pool_tier_counts.items():
        lower, upper = tier.edi_range(_N_BISECTION_FEVALS)
        edis.extend(np.linspace(max(lower, 1.0) + 0.1, upper - 0.1, count).tolist())
    np.random.default_rng(seed=8).shuffle(edis)
    return edis


@pytest.mark.parametrize(
    "selection_size, pool_tier_counts, counts_expected",
    [
        pytest.param(128, {A: 40, B: 40, C: 40, D: 40}, {A: 40, B: 40, C: 40, D: 40}, id="no_tier_below_quota"),
        pytest.param(256, {A: 64, B: 70, C: 66, D: 56}, {A: 64, B: 64, C: 64, D: 64}, id="through_a_tier"),
        pytest.param(128, {A: 10, B: 60, C: 40, D: 40}, {A: 32, B: 38, C: 40, D: 40}, id="lowest_tier_below_quota"),
        pytest.param(128, {A: 40, B: 31, C: 22, D: 46}, {A: 39, B: 32, C: 32, D: 36}, id="2_tiers_below_quota"),
        pytest.param(128, {A: 20, B: 40, C: 40, D: 28}, {A: 32, B: 32, C: 32, D: 32}, id="pool_of_the_size"),
    ],
)
def test_a_tier_below_its_quota_takes_candidates_from_the_nearest_surplus(
    selection_size, pool_tier_counts, counts_expected
):
    """Each tier below its quota takes its missing candidates from the nearest tier with a surplus:

    - with 56 of D and 66 of C for quotas of 64, D takes C's 2 surplus candidates; B's 6 surplus candidates move to C,
      and C passes 6 more to D, so C keeps 64;
    - with 31 of B and 22 of C, C has the larger shortfall and takes 10 from D first; B then takes 1 from A, because C
      has no surplus left.
    """
    # --- arrange ----------------------
    pool = _pool(_edis_of_tiers(pool_tier_counts))

    # --- act --------------------------
    tier_assignment = DifficultyTierAssignment.from_pool(pool, DifficultyTierQuotas(selection_size))

    # --- assert -----------------------
    assert Counter(tier_assignment.assigned_tiers.values()) == counts_expected
    assert list(tier_assignment.assigned_tiers) == list(pool.feature_matrix.problem_ids)


def test_with_surpluses_equally_near_the_closer_edi_moves_first():
    """C lacks 2 candidates, and B and D each have 2 in surplus.

    C first takes B's 19.9, whose EDI lies a factor 1.005 below C's range, ahead of D's 41, a factor 1.025 above it;
    then D's 41, ahead of B's 19.0, a factor 1.053 below.
    """
    # --- arrange ----------------------
    edis = [5.0] * 32 + [15.0] * 32 + [19.0, 19.9] + [30.0] * 30 + [41.0, 50.0] + [60.0] * 24 + [120.0] * 8
    pool = _pool(edis)

    # --- act --------------------------
    tier_assignment = DifficultyTierAssignment.from_pool(pool, DifficultyTierQuotas(128))

    # --- assert -----------------------
    assert Counter(tier_assignment.assigned_tiers.values()) == {A: 32, B: 33, C: 32, D: 33}
    assert tier_assignment.edi_range_by_tier == {
        A: (5.0, 5.0),
        B: (15.0, 19.0),
        C: (19.9, 41.0),
        D: (50.0, 120.0),
    }


def test_among_equal_edis_the_later_candidate_in_the_pool_moves_up():
    """D lacks 1 candidate, and C's 2 hardest candidates share the EDI 35; the later of the 2 in the pool goes to D, so
    the 2 tiers' EDI ranges meet at 35."""
    # --- arrange ----------------------
    edis = [5.0] * 32 + [15.0] * 32 + [35.0] + [30.0] * 31 + [35.0] + [60.0] * 31
    pool = _pool(edis)
    earlier_id, later_id = (pool.feature_matrix.problem_ids[idx] for idx in (64, 96))

    # --- act --------------------------
    tier_assignment = DifficultyTierAssignment.from_pool(pool, DifficultyTierQuotas(128))

    # --- assert -----------------------
    assert (tier_assignment.assigned_tiers[earlier_id], tier_assignment.assigned_tiers[later_id]) == (C, D)
    assert (tier_assignment.edi_range_by_tier[C], tier_assignment.edi_range_by_tier[D]) == (
        (30.0, 35.0),
        (35.0, 60.0),
    )


@pytest.mark.parametrize("seed", range(5))
def test_the_assigned_tiers_follow_the_edis_and_meet_every_quota(seed):
    """On random pools in which some EDIs repeat, the assigned tiers never decrease as the EDI rises, and every tier
    holds at least its quota."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed=seed)
    pool = _pool(np.round(2.0 * 80.0 ** rng.random(300), 0).tolist())
    quotas = DifficultyTierQuotas(256)

    # --- act --------------------------
    tier_assignment = DifficultyTierAssignment.from_pool(pool, quotas)

    # --- assert -----------------------
    tier_ranks = [list(DifficultyTier).index(tier) for tier in tier_assignment.assigned_tiers.values()]
    ranks_by_edi = np.array(tier_ranks)[np.argsort(pool.edis, kind="stable")]
    assert np.all(np.diff(ranks_by_edi) >= 0)
    tier_counts = Counter(tier_assignment.assigned_tiers.values())
    assert all(tier_counts[tier] >= quota for tier, quota in quotas.quota_by_tier.items())


def test_a_pool_smaller_than_the_selection_is_refused():
    """A pool of 120 candidates cannot fill a selection of 128."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="A pool of 120 candidates cannot fill a selection of 128"):
        DifficultyTierAssignment.from_pool(_pool([5.0] * 120), DifficultyTierQuotas(128))
