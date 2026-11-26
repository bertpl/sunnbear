"""`DifficultyTierCandidateGroup` holds the candidates of its difficulty tiers, labels itself by them, and refuses an
empty or repeated list of tiers."""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTier,
    DifficultyTierCandidateGroup,
)
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

A, B, C, D = DifficultyTier


@pytest.mark.parametrize(
    "tiers, label_expected",
    [
        pytest.param((C,), "C", id="1_tier"),
        pytest.param((B, A), "A+B", id="2_tiers_in_the_order_of_the_enum"),
    ],
)
def test_the_label_joins_the_tiers_in_the_order_of_the_enum(tiers, label_expected):
    """The label lists the group's tiers in the order of `DifficultyTier`, joined by ``+``."""
    # --- act / assert -----------------
    assert DifficultyTierCandidateGroup(tiers=tiers).label == label_expected


def test_the_members_are_the_candidates_of_the_groups_tiers():
    """With 40 bisection evaluations, the EDIs 5, 15, 30 and 60 fall in A, B, C and D, so the group of A and C holds
    the first and the third candidate."""
    # --- arrange ----------------------
    problem_ids = example_problem_ids(4)
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(problem_ids), values=np.zeros((4, 2))),
        edis=np.array([5.0, 15.0, 30.0, 60.0]),
        n_bisection_fevals=40,
    )

    # --- act --------------------------
    member_ids = DifficultyTierCandidateGroup(tiers=(C, A)).member_ids(pool)

    # --- assert -----------------------
    assert member_ids == [problem_ids[0], problem_ids[2]]


@pytest.mark.parametrize("tiers", [pytest.param((), id="no_tier"), pytest.param((A, A), id="tier_twice")])
def test_a_group_refuses_an_empty_or_repeated_list_of_tiers(tiers):
    """A group needs 1 or more tiers, each listed once."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="A group needs 1 or more tiers, each listed once"):
        DifficultyTierCandidateGroup(tiers=tiers)
