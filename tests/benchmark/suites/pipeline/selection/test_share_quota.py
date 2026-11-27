"""`ShareQuota` turns its shares into the counts of 1 selection, over the candidates of its group, and refuses shares
that give no whole number of candidates or that do not fit the range from 0 to 1."""

from fractions import Fraction

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    CountQuota,
    DifficultyTier,
    DifficultyTierCandidateGroup,
    ShareQuota,
)
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

_GROUP_OF_D = DifficultyTierCandidateGroup(tiers=(DifficultyTier.D,))


@pytest.mark.parametrize(
    "quota, min_count_expected, max_count_expected",
    [
        pytest.param(ShareQuota.exactly(_GROUP_OF_D, Fraction(1, 4)), 16, 16, id="exactly"),
        pytest.param(ShareQuota.at_least(_GROUP_OF_D, Fraction(1, 8)), 8, 64, id="at_least"),
    ],
)
def test_the_counts_of_a_selection_are_its_shares_of_the_size(quota, min_count_expected, max_count_expected):
    """In a selection of 64, a quarter is 16 candidates and an eighth 8; the quota counts the 2 candidates of D, whose
    EDIs of 60 and 100 lie above the 40 evaluations of bisection."""
    # --- arrange ----------------------
    problem_ids = example_problem_ids(4)
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(problem_ids), values=np.zeros((4, 2))),
        edis=np.array([5.0, 60.0, 30.0, 100.0]),
        n_bisection_fevals=40,
    )

    # --- act --------------------------
    count_quota = quota.for_selection(pool, selection_size=64)

    # --- assert -----------------------
    assert count_quota == CountQuota(
        group_label="D",
        member_ids=frozenset({problem_ids[1], problem_ids[3]}),
        min_count=min_count_expected,
        max_count=max_count_expected,
    )


def test_a_share_that_gives_no_whole_number_of_candidates_is_refused():
    """A quarter of a selection of 6 is 1.5 candidates."""
    # --- arrange ----------------------
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(example_problem_ids(6)), values=np.zeros((6, 2))),
        edis=np.full(6, 60.0),
        n_bisection_fevals=40,
    )

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"give no whole number of candidates in a selection of 6\.$"):
        ShareQuota.exactly(_GROUP_OF_D, Fraction(1, 4)).for_selection(pool, selection_size=6)


@pytest.mark.parametrize(
    "min_share, max_share",
    [
        pytest.param(Fraction(1, 2), Fraction(1, 4), id="min_above_max"),
        pytest.param(Fraction(-1, 4), Fraction(1, 4), id="negative"),
        pytest.param(Fraction(1, 4), Fraction(5, 4), id="above_1"),
    ],
)
def test_shares_outside_the_range_from_0_to_1_are_refused(min_share, max_share):
    """The shares must satisfy ``0 <= min_share <= max_share <= 1``."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"must satisfy 0 <= min_share <= max_share <= 1"):
        ShareQuota(group=_GROUP_OF_D, min_share=min_share, max_share=max_share)
