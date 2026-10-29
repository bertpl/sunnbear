"""`build_output_with_rejection_reports` splits a stage's rows into kept and rejected candidates, with their counts per
formula, and `summarize_rejections_per_formula` gives 1 line per formula with rejected candidates."""

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import (
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    REJECTIONS_PER_FORMULA_REPORT_NAME,
    RejectionReason,
    build_output_with_rejection_reports,
    summarize_rejections_per_formula,
)


def test_the_output_keeps_the_rows_without_a_reason_and_reports_the_others():
    """The output table holds the kept rows; the rejected rows lose the added column and gain their reason; the counts
    per formula follow each formula's first row."""
    # --- arrange ----------------------
    table = pl.DataFrame({"problem_id": ["f1.1.1.2", "f1.1.1.1[n=1.0]", "f1.1.1.1[n=2.0]"], "x": [None, 1.0, None]})
    results = [RejectionReason.BOUND_TO_WIDTH_RATIO, {"x": 1.0}, RejectionReason.BOUND_TO_WIDTH_RATIO]

    # --- act --------------------------
    output = build_output_with_rejection_reports(table, results, added_columns=["x"])

    # --- assert -----------------------
    assert output.table.rows() == [("f1.1.1.1[n=1.0]", 1.0)]
    rejected_candidates = output.reports[REJECTED_CANDIDATES_REPORT_NAME]
    assert rejected_candidates.schema == pl.Schema({"problem_id": pl.String(), **REJECTED_BY_SCHEMA})
    assert rejected_candidates.rows() == [
        ("f1.1.1.2", RejectionReason.BOUND_TO_WIDTH_RATIO.value),
        ("f1.1.1.1[n=2.0]", RejectionReason.BOUND_TO_WIDTH_RATIO.value),
    ]
    rejections_per_formula = output.reports[REJECTIONS_PER_FORMULA_REPORT_NAME]
    assert rejections_per_formula.select("formula_id", "n_candidates", "n_kept", "bound_to_width_ratio").rows() == [
        ("f1.1.1.2", 1, 0, 1),
        ("f1.1.1.1", 2, 1, 1),
    ]


def test_the_summary_gives_1_line_per_formula_with_rejected_candidates():
    """Only a formula with a rejected candidate gets a line, which counts the rejections of each reason that rejected
    any."""
    # --- arrange ----------------------
    rejection_counts = {reason.value: [0, 0] for reason in RejectionReason}
    rejection_counts[RejectionReason.BOUND_TO_WIDTH_RATIO.value] = [1, 0]
    rejection_counts[RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0.value] = [2, 0]
    rejections_per_formula = pl.DataFrame(
        {"formula_id": ["f1.1.1.1", "f1.1.1.2"], "n_candidates": [4, 2], "n_kept": [1, 2], **rejection_counts}
    )

    # --- act --------------------------
    lines = summarize_rejections_per_formula(rejections_per_formula)

    # --- assert -----------------------
    assert lines == [
        "formulas with rejected candidates: 1 of 2",
        "  f1.1.1.1: 1 of 4 candidates kept; bound_to_width_ratio: 1, calibration_no_finite_sign_change_at_0: 2",
    ]
