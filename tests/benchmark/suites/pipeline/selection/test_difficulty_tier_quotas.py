"""`DifficultyTierQuotas.resolve` merges quotas until the candidates can meet each of them, and
`DifficultyTierQuotas.check_selection` checks that a selection has the size and meets each quota."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyTier, DifficultyTierQuotas

A, B, C, DA, DB = DifficultyTier


@pytest.mark.parametrize(
    "pool_tier_counts, counts_expected",
    [
        pytest.param(
            {A: 40, B: 40, C: 40, DA: 30, DB: 10},
            {frozenset({A}): 32, frozenset({B}): 32, frozenset({C}): 32, frozenset({DA}): 24, frozenset({DB}): 8},
            id="no_merge",
        ),
        pytest.param(
            {A: 40, B: 40, C: 40, DA: 40},
            {frozenset({A}): 32, frozenset({B}): 32, frozenset({C}): 32, frozenset({DA, DB}): 32},
            id="a_short_db_merges_with_da",
        ),
        pytest.param(
            {A: 10, B: 60, C: 40, DA: 30, DB: 10},
            {frozenset({A, B}): 64, frozenset({C}): 32, frozenset({DA}): 24, frozenset({DB}): 8},
            id="a_short_a_merges_with_b",
        ),
        pytest.param(
            {A: 40, B: 10, C: 60, DA: 30, DB: 10},
            {frozenset({A}): 32, frozenset({B, C}): 64, frozenset({DA}): 24, frozenset({DB}): 8},
            id="a_tie_goes_to_the_higher_tier",
        ),
        pytest.param(
            {A: 40, B: 31, C: 22, DA: 40, DB: 10},
            {frozenset({A, B}): 64, frozenset({C, DA}): 56, frozenset({DB}): 8},
            id="the_largest_shortfall_merges_first",
        ),
        pytest.param({A: 128}, {frozenset(DifficultyTier): 128}, id="all_tiers_in_1_group"),
    ],
)
def test_short_quotas_merge_with_a_neighbor_until_each_can_be_met(pool_tier_counts, counts_expected):
    """For a selection of 128, every tier starts with its share: 32 each for A, B and C, 24 for Da, 8 for Db. A quota
    that asks for more candidates than its group holds merges with its neighbor with the smaller quota, a tie going to
    the higher tier. With 31 of B and 22 of C, C is 10 short and merges first, with Da, whose quota is smaller than
    B's; B, then 1 short, merges with A, because its other neighbor's quota, C and Da's 56, is larger."""
    # --- act --------------------------
    tier_quotas = DifficultyTierQuotas.resolve(128, pool_tier_counts)

    # --- assert -----------------------
    assert tier_quotas.counts == counts_expected
    assert list(tier_quotas.counts) == list(counts_expected)


@pytest.mark.parametrize(
    "size, pool_tier_counts, message",
    [
        pytest.param(
            100, {A: 200}, "A selection of 100 candidates gives some tier a quota that is not whole", id="size"
        ),
        pytest.param(128, {A: 100, B: 20}, "120 candidates cannot fill a selection of 128", id="pool"),
    ],
)
def test_quotas_are_refused_for_a_size_without_whole_quotas_or_too_few_candidates(size, pool_tier_counts, message):
    """A size that is not a multiple of 16 gives Db a quota that is not whole, and a pool smaller than the selection can
    meet no quotas."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        DifficultyTierQuotas.resolve(size, pool_tier_counts)


_QUOTAS_WITH_MERGED_D = DifficultyTierQuotas(
    counts={frozenset({A}): 32, frozenset({B}): 32, frozenset({C}): 32, frozenset({DA, DB}): 32}
)


@pytest.mark.parametrize(
    "selected_tiers, message",
    [
        pytest.param([A] * 32 + [B] * 32 + [C] * 32 + [DA] * 30 + [DB] * 2, None, id="met"),
        pytest.param([A] * 33 + [B] * 31 + [C] * 32 + [DA] * 32, r"A: 33 of 32; B: 31 of 32\.", id="unmet"),
        pytest.param([A] * 32 + [B] * 32 + [C] * 32 + [DA] * 24, r"120 candidates .* Da and Db: 24 of 32\.", id="few"),
    ],
)
def test_a_selection_must_have_the_size_and_meet_every_quota(selected_tiers, message):
    """A selection of the right size that meets every quota passes, however a merged quota splits between its tiers;
    one that misses a quota or the size stops the pipeline, with a message that names each unmet quota and the
    selection's count."""
    # --- act / assert -----------------
    if message is None:
        _QUOTAS_WITH_MERGED_D.check_selection(selected_tiers)
    else:
        with pytest.raises(PipelineStopError, match=message):
            _QUOTAS_WITH_MERGED_D.check_selection(selected_tiers)


def test_the_quotas_read_back_from_their_json_values_equal_the_original():
    """Quotas written as JSON values and read back hold the same groups and counts, in the same order."""
    # --- act --------------------------
    read_back = DifficultyTierQuotas.from_json_values(_QUOTAS_WITH_MERGED_D.to_json_values())

    # --- assert -----------------------
    assert read_back == _QUOTAS_WITH_MERGED_D
    assert list(read_back.counts) == list(_QUOTAS_WITH_MERGED_D.counts)
