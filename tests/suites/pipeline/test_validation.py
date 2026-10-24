"""`validate_candidates` keeps every candidate and records the check that rejected it."""

import polars as pl
import pytest

from sunnbear._core.suites.pipeline.generation import CANDIDATES_SCHEMA
from sunnbear._core.suites.pipeline.validation import VALIDATED_CANDIDATES_SCHEMA, validate_candidates


@pytest.mark.parametrize(
    "a, b, rejected_by_expected",
    [
        pytest.param(-1.0, 1.0, "", id="ratio_0.5"),
        pytest.param(99.0, 100.0, "", id="ratio_100_at_the_limit"),
        pytest.param(100.0, 101.0, "interval_ratio", id="ratio_101_right_of_0"),
        pytest.param(-101.0, -100.0, "interval_ratio", id="ratio_101_left_of_0"),
    ],
)
def test_the_interval_check_rejects_an_interval_whose_ratio_exceeds_100(a, b, rejected_by_expected):
    """A candidate whose ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds 100 is rejected by the interval check, on
    either side of 0; one at the limit is valid."""
    # --- arrange ----------------------
    candidates = pl.DataFrame({"function_id": ["f2.1.1[p1=0.2]"], "a": [a], "b": [b]}, schema=CANDIDATES_SCHEMA)

    # --- act --------------------------
    validated = validate_candidates(candidates)

    # --- assert -----------------------
    assert validated.schema == pl.Schema(VALIDATED_CANDIDATES_SCHEMA)
    assert validated.rows() == [("f2.1.1[p1=0.2]", a, b, rejected_by_expected)]
