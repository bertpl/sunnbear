"""`DifficultyTier` meets these rules:

- `DifficultyTier.from_edi` buckets an EDI by its ratio to `n_bisection_fevals`;
- each tier's EDI range starts where the range of the tier before it ends;
- an EDI's ratio distance to a range is the factor by which the EDI lies outside the range;
- each tier fills its fixed share of the Core.
"""

from fractions import Fraction

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
    """With 40 bisection evaluations, the tiers start at the EDIs 10, 20 and 40, and an EDI of `max_fevals`, 160, falls
    in D."""
    # --- act / assert -----------------
    assert DifficultyTier.from_edi(edi, n_bisection_fevals=40) is difficulty_tier_expected


def test_each_tiers_edi_range_starts_where_the_one_before_ends():
    """With 40 bisection evaluations, the tiers' EDI ranges run from 0 to 10, 20, 40 and 160."""
    # --- act / assert -----------------
    assert [tier.edi_range(40) for tier in DifficultyTier] == [(0, 10), (10, 20), (20, 40), (40, 160)]


@pytest.mark.parametrize(
    "edi, distance_expected",
    [
        pytest.param(16.0, 1.25, id="below"),
        pytest.param(30.0, 1.0, id="inside"),
        pytest.param(60.0, 1.5, id="above"),
    ],
)
def test_the_ratio_distance_is_the_factor_outside_the_range(edi, distance_expected):
    """With 40 bisection evaluations, C's range runs from 20 to 40: 16 lies a factor 1.25 below it, and 60 a factor 1.5
    above it."""
    # --- act / assert -----------------
    assert DifficultyTier.C.edi_ratio_distance(edi, 40) == distance_expected


def test_each_tier_fills_a_quarter_of_the_core():
    """Each tier fills a quarter of the Core."""
    # --- act / assert -----------------
    assert [difficulty_tier.core_share for difficulty_tier in DifficultyTier] == [Fraction(1, 4)] * 4
