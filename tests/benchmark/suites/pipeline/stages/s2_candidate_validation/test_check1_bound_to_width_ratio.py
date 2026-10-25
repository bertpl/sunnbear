"""`exceeds_max_bound_to_width_ratio` is true for a candidate whose bound-to-width ratio exceeds 100."""

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation.check1_bound_to_width_ratio import (
    exceeds_max_bound_to_width_ratio,
)


@pytest.mark.parametrize(
    "a, b, is_ratio_too_large_expected",
    [
        pytest.param(-1.0, 1.0, False, id="ratio_0.5"),
        pytest.param(99.0, 100.0, False, id="ratio_100_at_the_limit"),
        pytest.param(100.0, 101.0, True, id="ratio_101_right_of_0"),
        pytest.param(-101.0, -100.0, True, id="ratio_101_left_of_0"),
    ],
)
def test_the_bound_to_width_ratio_check_rejects_an_interval_whose_ratio_exceeds_100(a, b, is_ratio_too_large_expected):
    """The check rejects a candidate whose ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds 100, on either side of 0;
    one at the limit passes."""
    # --- act --------------------------
    is_ratio_too_large = pl.DataFrame({"a": [a], "b": [b]}).select(exceeds_max_bound_to_width_ratio()).item()

    # --- assert -----------------------
    assert is_ratio_too_large is is_ratio_too_large_expected
