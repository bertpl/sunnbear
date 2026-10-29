"""The stages of the benchmark suite pipeline that reject candidates name each rejection with a `RejectionReason`.

`build_output_with_rejection_reports` builds such a stage's output: the candidates that the stage keeps, and 2 reports
on the others, `REJECTED_CANDIDATES_REPORT_NAME` and `REJECTIONS_PER_FORMULA_REPORT_NAME`, which have the same columns
for every stage. `summarize_rejections_per_formula` turns the second report into lines of text.
"""

from collections.abc import Collection, Sequence
from enum import StrEnum

import polars as pl

from sunnbear._core.problems.core import ProblemId

from .stage import PipelineStageOutput


# ==================================================================================================
#  RejectionReason
# ==================================================================================================
class RejectionReason(StrEnum):
    """A `RejectionReason` names the check that rejected a candidate, or for some checks the condition that failed.

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
    # At 1 of the sampled tuples, f raises during snuffled's analysis.
    SNUFFLED_F_RAISES = "snuffled_f_raises"
    # At 1 of the sampled tuples, the snuffled diagnostic named by the part of the member's name after `SNUFFLED_` is
    # above 0.
    SNUFFLED_NAN_VALUES_DETECTED = "snuffled_nan_values_detected"
    SNUFFLED_INF_VALUES_DETECTED = "snuffled_inf_values_detected"
    SNUFFLED_NO_ZEROS_DETECTED = "snuffled_no_zeros_detected"
    SNUFFLED_INTERVAL_NOT_BRACKETING_READY = "snuffled_interval_not_bracketing_ready"
    SNUFFLED_ALL_ROOTS_TOO_CLOSE_TO_EDGE = "snuffled_all_roots_too_close_to_edge"
    # At 1 of the sampled tuples, snuffled's `MAX_ZERO_WIDTH` exceeds `MAX_ZERO_WIDTH_IN_XTOL` times the tuple's `xtol`.
    SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE = "snuffled_max_zero_width_too_large"


# The report `REJECTED_CANDIDATES_REPORT_NAME` adds this column to each rejected candidate: its `RejectionReason`.
REJECTED_BY_SCHEMA: dict[str, pl.DataType] = {"rejected_by": pl.Enum([reason.value for reason in RejectionReason])}
REJECTED_CANDIDATES_REPORT_NAME = "rejected_candidates"
REJECTIONS_PER_FORMULA_REPORT_NAME = "rejections_per_formula"


# ==================================================================================================
#  Stage output and summary
# ==================================================================================================
def build_output_with_rejection_reports(
    table: pl.DataFrame, rejection_reasons: Sequence[RejectionReason | None], *, added_columns: Collection[str]
) -> PipelineStageOutput:
    """Return the output of a stage that rejects candidates, with its 2 reports on the rejected candidates.

    Args:
        table: Every row of the stage's input table, with the columns that the stage adds; on a rejected candidate's
            row, the added columns hold nulls.
        rejection_reasons: The `RejectionReason` of each row of `table`, in its order, or ``None`` for a candidate that
            the stage keeps.
        added_columns: The names of the columns that the stage adds to its input table.

    Returns:
        The stage's output, which holds:

        - the output table: the rows of `table` whose reason is ``None``;
        - the report `REJECTED_CANDIDATES_REPORT_NAME`: the other rows, without `added_columns`, and with the columns of
          `REJECTED_BY_SCHEMA`;
        - the report `REJECTIONS_PER_FORMULA_REPORT_NAME`: 1 row per formula, in the order of each formula's first
          row in `table`, with the columns ``formula_id``, ``n_candidates``, ``n_valid``, and 1 count per
          `RejectionReason`, named after its value.
    """
    table_with_reasons = table.with_columns(
        pl.Series(
            "rejected_by",
            [None if reason is None else reason.value for reason in rejection_reasons],
            dtype=REJECTED_BY_SCHEMA["rejected_by"],
        )
    )
    is_kept = pl.col("rejected_by").is_null()
    return PipelineStageOutput(
        table=table_with_reasons.filter(is_kept).drop(list(REJECTED_BY_SCHEMA)),
        reports={
            REJECTED_CANDIDATES_REPORT_NAME: table_with_reasons.filter(~is_kept).drop(list(added_columns)),
            REJECTIONS_PER_FORMULA_REPORT_NAME: _count_rejections_per_formula(table_with_reasons),
        },
    )


def summarize_rejections_per_formula(rejections_per_formula: pl.DataFrame) -> list[str]:
    """Return a line that counts the formulas with rejected candidates, then 1 line per such formula.

    `rejections_per_formula` is a stage's report `REJECTIONS_PER_FORMULA_REPORT_NAME`. A formula's line gives its number
    of candidates, how many of them the stage keeps, and the number of rejected candidates per `RejectionReason` that
    rejected any.
    """
    formulas_with_rejections = rejections_per_formula.filter(pl.col("n_valid") < pl.col("n_candidates"))
    lines = [f"formulas with rejected candidates: {formulas_with_rejections.height} of {rejections_per_formula.height}"]
    for row in formulas_with_rejections.iter_rows(named=True):
        rejections = ", ".join(
            f"{reason.value}: {row[reason.value]}" for reason in RejectionReason if row[reason.value] > 0
        )
        lines.append(f"  {row['formula_id']}: {row['n_valid']} of {row['n_candidates']} candidates valid; {rejections}")
    return lines


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _count_rejections_per_formula(table: pl.DataFrame) -> pl.DataFrame:
    """Return the report `REJECTIONS_PER_FORMULA_REPORT_NAME` of `table`, which holds a ``rejected_by`` column."""
    formula_ids = [ProblemId.from_string(problem_id).formula_id for problem_id in table["problem_id"]]
    return (
        table.with_columns(formula_id=pl.Series(formula_ids, dtype=pl.String()))
        .group_by("formula_id", maintain_order=True)
        .agg(
            n_candidates=pl.len(),
            n_valid=pl.col("rejected_by").is_null().sum(),
            **{reason.value: (pl.col("rejected_by") == reason.value).sum() for reason in RejectionReason},
        )
    )
