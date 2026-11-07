"""`DifficultyTier.from_edi` buckets an EDI by its ratio to `n_bisection_fevals`, and the tiers' Core shares sum to
1."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyTier


@pytest.mark.parametrize(
    "edi, difficulty_tier_expected",
    [
        (2.0, DifficultyTier.A),
        (9.99, DifficultyTier.A),
        (10.0, DifficultyTier.B),
        (20.0, DifficultyTier.C),
        (39.99, DifficultyTier.C),
        (40.0, DifficultyTier.DA),
        (80.0, DifficultyTier.DB),
        (160.0, DifficultyTier.DB),
    ],
)
def test_the_tier_follows_the_edi_relative_to_bisections_count(edi, difficulty_tier_expected):
    """With 40 bisection evaluations, the tiers start at the EDIs 10, 20, 40 and 80, and an EDI of `max_fevals`, 160,
    falls in Db."""
    # --- act / assert -----------------
    assert DifficultyTier.from_edi(edi, n_bisection_fevals=40) is difficulty_tier_expected


def test_the_core_shares_sum_to_1():
    """A, B and C fill a quarter of the Core each, Da 3/16 and Db 1/16."""
    # --- act / assert -----------------
    assert [difficulty_tier.core_share * 16 for difficulty_tier in DifficultyTier] == [4, 4, 4, 3, 1]
