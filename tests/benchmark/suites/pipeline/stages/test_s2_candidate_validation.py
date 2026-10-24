"""`CandidateValidationStage` keeps the valid candidates, and reports each rejected candidate with the check that
rejected it."""

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.stages.s1_candidate_generation import CANDIDATES_SCHEMA
from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation import (
    REJECTED_CANDIDATES_SCHEMA,
    CandidateValidationStage,
)
from sunnbear._core.utils.worker_pool import WorkerPool

_FUNCTION_ID = "f2.1.1[p1=0.2]"


@pytest.mark.parametrize(
    "a, b, valid_rows_expected, rejected_rows_expected",
    [
        pytest.param(-1.0, 1.0, [(_FUNCTION_ID, -1.0, 1.0)], [], id="ratio_0.5"),
        pytest.param(99.0, 100.0, [(_FUNCTION_ID, 99.0, 100.0)], [], id="ratio_100_at_the_limit"),
        pytest.param(
            100.0, 101.0, [], [(_FUNCTION_ID, 100.0, 101.0, "bound_to_width_ratio")], id="ratio_101_right_of_0"
        ),
        pytest.param(
            -101.0, -100.0, [], [(_FUNCTION_ID, -101.0, -100.0, "bound_to_width_ratio")], id="ratio_101_left_of_0"
        ),
    ],
)
def test_the_bound_to_width_ratio_check_rejects_an_interval_whose_ratio_exceeds_100(
    a, b, valid_rows_expected, rejected_rows_expected
):
    """A candidate whose ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds 100 moves from the output table to the report
    ``rejected_candidates``, with its reason, on either side of 0; one at the limit is valid."""
    # --- arrange ----------------------
    candidates = pl.DataFrame({"function_id": [_FUNCTION_ID], "a": [a], "b": [b]}, schema=CANDIDATES_SCHEMA)

    # --- act --------------------------
    output = CandidateValidationStage().compute_output(candidates, worker_pool=WorkerPool(n_workers=1, module_names=[]))

    # --- assert -----------------------
    rejected_candidates = output.reports["rejected_candidates"]
    assert output.table.schema == pl.Schema(CANDIDATES_SCHEMA)
    assert rejected_candidates.schema == pl.Schema(REJECTED_CANDIDATES_SCHEMA)
    assert output.table.rows() == valid_rows_expected
    assert rejected_candidates.rows() == rejected_rows_expected
