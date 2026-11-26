"""`CountQuota` counts the selected candidates of its group in its fulfillment."""

from sunnbear._core.benchmark.suites.pipeline.selection import CountQuota, QuotaFulfillment
from tests.benchmark.suites.pipeline.example_states import example_problem_ids

_PROBLEM_IDS = example_problem_ids(6)


def test_the_fulfillment_counts_the_selected_candidates_of_the_group():
    """Of the 3 candidates of the group, 2 are among the 4 selected candidates."""
    # --- arrange ----------------------
    count_quota = CountQuota(label="A", problem_ids=frozenset(_PROBLEM_IDS[:3]), min_count=1, max_count=2)

    # --- act --------------------------
    fulfillment = count_quota.fulfillment(_PROBLEM_IDS[1:5])

    # --- assert -----------------------
    assert fulfillment == QuotaFulfillment(label="A", min_count=1, max_count=2, n_selected=2)
