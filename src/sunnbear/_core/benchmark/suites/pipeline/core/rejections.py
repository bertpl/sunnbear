"""The stages of the benchmark suite pipeline that reject candidates name each rejection with a `RejectionReason`.

`PipelineStage._build_output_with_rejection_reports` builds such a stage's output: the candidates that the stage
keeps, and 2 reports on the rejected candidates, `REJECTED_CANDIDATES_REPORT_NAME` and
`REJECTIONS_PER_FORMULA_REPORT_NAME`, which have the same columns for every stage. `summarize_rejections_per_formula`
turns the second report into lines of text.
"""

from enum import StrEnum

import polars as pl


# ==================================================================================================
#  RejectionReason
# ==================================================================================================
class RejectionReason(StrEnum):
    """A `RejectionReason` names the check, or the condition, that made a stage reject a candidate.

    The calibration reasons follow the steps of `calibrate_c_range`; the reasons whose names start with `SNUFFLED_` name
    the conditions under which `extract_properties_or_rejection_reason` rejects a candidate, listed in the order in
    which that function tests them.
    """

    BOUND_TO_WIDTH_RATIO = "bound_to_width_ratio"
    # f(a, 0) and f(b, 0) are not both finite and nonzero, with opposite signs.
    CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0 = "calibration_no_finite_sign_change_at_0"
    # The condition fails at the first probe, on either side of c = 0.
    CALIBRATION_FAILS_AT_FIRST_PROBE = "calibration_fails_at_first_probe"
    # The condition still holds after the last doubling of abs(c), on either side of c = 0.
    CALIBRATION_NO_BOUND_FOUND = "calibration_no_bound_found"
    # The condition still fails at 1 of the benchmark's c-values after the last return to step 4 of the search.
    CALIBRATION_FAILS_AT_BENCHMARK_C_VALUES = "calibration_fails_at_benchmark_c_values"
    # The c-range is narrower than `MIN_C_RANGE_WIDTH` at step 6 of the search.
    CALIBRATION_C_RANGE_TOO_NARROW = "calibration_c_range_too_narrow"
    # At 1 of the tuples, `Bisection` does not converge in exactly `DEFAULT_N_BISECTION_FEVALS` evaluations.
    BISECTION_COUNT_NOT_EXACT = "bisection_count_not_exact"
    # At 1 of the tuples of snuffled's analyses, f raises during the analysis.
    SNUFFLED_F_RAISES = "snuffled_f_raises"
    # At 1 of the tuples of snuffled's analyses, the snuffled diagnostic of the same name, without the prefix
    # `SNUFFLED_`, is above 0.
    SNUFFLED_NAN_VALUES_DETECTED = "snuffled_nan_values_detected"
    SNUFFLED_INF_VALUES_DETECTED = "snuffled_inf_values_detected"
    SNUFFLED_NO_ZEROS_DETECTED = "snuffled_no_zeros_detected"
    SNUFFLED_INTERVAL_NOT_BRACKETING_READY = "snuffled_interval_not_bracketing_ready"
    SNUFFLED_ALL_ROOTS_TOO_CLOSE_TO_EDGE = "snuffled_all_roots_too_close_to_edge"
    # At 1 of the tuples of snuffled's analyses, snuffled's `MAX_ZERO_WIDTH` exceeds `MAX_ZERO_WIDTH_IN_XTOL` times the
    # tuple's `xtol`.
    SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE = "snuffled_max_zero_width_too_large"
    # 1 of the solves of a characterization stage ends with `SolveStatus.FUNCTION_ERROR`: f raises, or returns a value
    # that is not finite, at an x inside the interval.
    FUNCTION_ERROR = "function_error"


# The report `REJECTED_CANDIDATES_REPORT_NAME` adds this column to each rejected candidate: its `RejectionReason`.
REJECTED_BY_SCHEMA: dict[str, pl.DataType] = {"rejected_by": pl.Enum([reason.value for reason in RejectionReason])}
REJECTED_CANDIDATES_REPORT_NAME = "rejected_candidates"
REJECTIONS_PER_FORMULA_REPORT_NAME = "rejections_per_formula"


# ==================================================================================================
#  Summary
# ==================================================================================================
def summarize_rejections_per_formula(rejections_per_formula: pl.DataFrame) -> list[str]:
    """Return a line that counts the formulas with rejected candidates, then 1 line per such formula.

    `rejections_per_formula` is a stage's report `REJECTIONS_PER_FORMULA_REPORT_NAME`. A formula's line gives its number
    of candidates, how many of them the stage keeps, and, for each `RejectionReason` that rejected at least 1 of its
    candidates, the number of candidates that it rejected.
    """
    formulas_with_rejections = rejections_per_formula.filter(pl.col("n_kept") < pl.col("n_candidates"))
    lines = [f"formulas with rejected candidates: {formulas_with_rejections.height} of {rejections_per_formula.height}"]
    for row in formulas_with_rejections.iter_rows(named=True):
        rejections = ", ".join(
            f"{reason.value}: {row[reason.value]}" for reason in RejectionReason if row[reason.value] > 0
        )
        lines.append(f"  {row['formula_id']}: {row['n_kept']} of {row['n_candidates']} candidates kept; {rejections}")
    return lines
