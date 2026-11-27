"""`CountQuota` counts the selected candidates of its group in its fulfillment, and becomes a max-div constraint whose
smallest count is at most the size of its group, or no constraint for a group without candidates."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.selection import CountQuota, QuotaFulfillment
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

_PROBLEM_IDS = example_problem_ids(6)


def test_the_fulfillment_counts_the_selected_candidates_of_the_group():
    """Of the 3 candidates of the group, 2 are among the 4 selected candidates."""
    # --- arrange ----------------------
    count_quota = CountQuota(group_label="A", member_ids=frozenset(_PROBLEM_IDS[:3]), min_count=1, max_count=2)

    # --- act --------------------------
    fulfillment = count_quota.fulfillment(_PROBLEM_IDS[1:5])

    # --- assert -----------------------
    assert fulfillment == QuotaFulfillment(group_label="A", min_count=1, max_count=2, n_selected_in_group=2)


@pytest.mark.parametrize(
    "min_count, min_count_expected",
    [
        pytest.param(2, 2, id="smallest_count_within_the_group"),
        pytest.param(5, 3, id="smallest_count_above_the_group_size"),
    ],
)
def test_the_constraint_lowers_the_smallest_count_to_the_group_size(min_count, min_count_expected):
    """The constraint covers the rows of the group's 3 candidates, and its smallest count is at most 3."""
    # --- arrange ----------------------
    count_quota = CountQuota(group_label="A", member_ids=frozenset(_PROBLEM_IDS[:3]), min_count=min_count, max_count=6)
    row_index_by_problem_id = {problem_id: idx for idx, problem_id in enumerate(_PROBLEM_IDS)}

    # --- act --------------------------
    constraint = count_quota.to_constraint(row_index_by_problem_id)

    # --- assert -----------------------
    assert (set(constraint.int_set), constraint.min_count, constraint.max_count) == ({0, 1, 2}, min_count_expected, 6)


def test_a_group_without_candidates_gives_no_constraint():
    """A quota whose group holds no candidates has no max-div constraint."""
    # --- arrange ----------------------
    count_quota = CountQuota(group_label="D", member_ids=frozenset(), min_count=1, max_count=2)

    # --- act / assert -----------------
    assert count_quota.to_constraint({}) is None
