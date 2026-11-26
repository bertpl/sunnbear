"""`QuotaFulfillment` is met when its number of selected candidates lies from the quota's smallest up to its largest
count."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.selection import QuotaFulfillment


@pytest.mark.parametrize(
    "n_selected, is_met_expected",
    [
        pytest.param(0, False, id="below"),
        pytest.param(1, True, id="at_the_smallest_count"),
        pytest.param(2, True, id="at_the_largest_count"),
        pytest.param(3, False, id="above"),
    ],
)
def test_a_fulfillment_is_met_from_the_smallest_up_to_the_largest_count(n_selected, is_met_expected):
    """A quota of 1 up to 2 candidates is met by 1 or 2 selected candidates, and missed by 0 or 3."""
    # --- act / assert -----------------
    assert QuotaFulfillment(label="A", min_count=1, max_count=2, n_selected=n_selected).is_met is is_met_expected
