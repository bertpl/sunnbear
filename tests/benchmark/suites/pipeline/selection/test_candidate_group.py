"""The kinds of `CandidateGroup` meet these checks:

- `DifficultyTierCandidateGroup` holds the candidates of its difficulty tiers, labels itself by them, and refuses an
  empty or repeated list of tiers;
- `FormulaCategoryCandidateGroup` holds the candidates whose formulas lie at any depth below its category, and labels
  itself by the category's name.
"""

import numpy as np
import pytest

from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureMatrix
from sunnbear._core.benchmark.suites.pipeline.selection import (
    CandidatePool,
    DifficultyTier,
    DifficultyTierCandidateGroup,
    FormulaCategoryCandidateGroup,
)
from sunnbear._core.problems.core import ProblemId
from tests.benchmark.suites.pipeline.example_states import example_problem_ids
from tests.problems.helpers.example_taxonomy_nodes import define_category_cls

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


@pytest.mark.usefixtures("isolated_formula_registry")
def test_a_formula_category_group_holds_the_candidates_below_its_category_at_any_depth():
    """The group of category 99.5 holds the candidates of formulas 99.5.1 and 99.5.2.1, and not those of formulas
    99.50.1 and 1.2.3; its label is the category's name."""
    # --- arrange ----------------------
    category = define_category_cls((99, 5))
    problem_ids = [
        ProblemId.from_string(text) for text in ("f99.5.1[p=1]", "f99.50.1[p=1]", "f99.5.2.1[p=1]", "f1.2.3[p=1]")
    ]
    pool = CandidatePool(
        feature_matrix=FeatureMatrix(problem_ids=tuple(problem_ids), values=np.zeros((4, 2))),
        edis=np.full(4, 10.0),
        n_bisection_fevals=40,
    )
    group = FormulaCategoryCandidateGroup(category=category)

    # --- act --------------------------
    member_ids = group.member_ids(pool)

    # --- assert -----------------------
    assert (member_ids, group.label) == ([problem_ids[0], problem_ids[2]], "Example 99.5")
