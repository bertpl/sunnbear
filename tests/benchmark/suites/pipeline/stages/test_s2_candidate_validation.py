"""`CandidateValidationStage` keeps every candidate and records the check that rejected it."""

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.stages.s1_candidate_generation import CANDIDATES_SCHEMA
from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation import (
    CHECKED_CANDIDATES_SCHEMA,
    CandidateValidationStage,
)


@pytest.mark.parametrize(
    "a, b, rejected_by_expected",
    [
        pytest.param(-1.0, 1.0, "", id="ratio_0.5"),
        pytest.param(99.0, 100.0, "", id="ratio_100_at_the_limit"),
        pytest.param(100.0, 101.0, "bound_to_width_ratio", id="ratio_101_right_of_0"),
        pytest.param(-101.0, -100.0, "bound_to_width_ratio", id="ratio_101_left_of_0"),
    ],
)
def test_the_bound_to_width_ratio_check_rejects_an_interval_whose_ratio_exceeds_100(a, b, rejected_by_expected):
    """A candidate whose ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds 100 is rejected by the bound-to-width ratio
    check, on either side of 0; one at the limit is valid."""
    # --- arrange ----------------------
    candidates = pl.DataFrame({"function_id": ["f2.1.1[p1=0.2]"], "a": [a], "b": [b]}, schema=CANDIDATES_SCHEMA)

    # --- act --------------------------
    checked_candidates = CandidateValidationStage().compute_output(candidates)

    # --- assert -----------------------
    assert checked_candidates.schema == pl.Schema(CHECKED_CANDIDATES_SCHEMA)
    assert checked_candidates.rows() == [("f2.1.1[p1=0.2]", a, b, rejected_by_expected)]
