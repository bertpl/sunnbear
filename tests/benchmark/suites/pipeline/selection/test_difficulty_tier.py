"""`DifficultyTier` meets these rules:

- `DifficultyTier.from_edi` buckets an EDI by its ratio to `n_bisection_fevals`;
- each tier's EDI range starts where the range of the tier before it ends.
"""

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
        (40.0, DifficultyTier.D),
        (80.0, DifficultyTier.D),
        (160.0, DifficultyTier.D),
    ],
)
def test_the_tier_follows_the_edi_relative_to_bisections_count(edi, difficulty_tier_expected):
    """With 40 bisection evaluations, tiers B, C and D start at the EDIs 10, 20 and 40, and an EDI of `max_fevals`, 160,
    falls in D."""
    # --- act / assert -----------------
    assert DifficultyTier.from_edi(edi, n_bisection_fevals=40) is difficulty_tier_expected


def test_each_tiers_edi_range_starts_where_the_one_before_ends():
    """With 40 bisection evaluations, the tiers' EDI ranges run from 0 to 10, 20, 40 and 160."""
    # --- act / assert -----------------
    assert [tier.edi_range(40) for tier in DifficultyTier] == [(0, 10), (10, 20), (20, 40), (40, 160)]
