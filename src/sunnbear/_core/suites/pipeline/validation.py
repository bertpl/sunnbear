"""Validation, the second stage of the suite pipeline, runs the validation checks on every candidate.

The checks run in sequence, cheapest first, and a candidate is rejected by the first check that it
fails. The output holds every candidate of the candidate generation stage, with the columns of
`VALIDATION_SCHEMA`: its ``rejected_by`` column names the check that rejected the candidate, as a
`RejectionReason`, or holds ``""`` for a valid candidate. Rejected candidates stay in the output, so
that the reasons can be counted per formula.

The interval check, the first check, rejects a candidate whose interval lies far from 0 relative to its
width: its ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds `MAX_INTERVAL_RATIO`. Rounding in the
interval bounds can change bisection's evaluation count at the tolerances near the ones where that count
changes, and the share of tolerances at risk grows with the ratio. The limit is stricter than the one of
`compute_xtol_range`, which accepts ratios up to 1024 for users' own functions.
"""

from enum import StrEnum

import polars as pl

from .generation import CANDIDATES_SCHEMA

# A candidate whose interval ratio exceeds this limit is rejected by the interval check.
MAX_INTERVAL_RATIO = 100.0


# ==================================================================================================
#  RejectionReason
# ==================================================================================================
class RejectionReason(StrEnum):
    """A `RejectionReason` names the validation check that rejected a candidate."""

    INTERVAL_RATIO = "interval_ratio"


VALIDATION_SCHEMA: dict[str, pl.DataType] = {
    **CANDIDATES_SCHEMA,
    "rejected_by": pl.Enum(["", *RejectionReason]),
}


# ==================================================================================================
#  validate_candidates
# ==================================================================================================
def validate_candidates(candidates: pl.DataFrame) -> pl.DataFrame:
    """Return `candidates` with a ``rejected_by`` column: the check that rejected each one, or ``""`` if none did.

    Args:
        candidates: The output of candidate generation, with the columns of `CANDIDATES_SCHEMA`.
    """
    interval_ratio = pl.max_horizontal(pl.col("a").abs(), pl.col("b").abs()) / (pl.col("b") - pl.col("a"))
    rejected_by = (
        pl.when(interval_ratio > MAX_INTERVAL_RATIO).then(pl.lit(RejectionReason.INTERVAL_RATIO)).otherwise(pl.lit(""))
    )
    return candidates.with_columns(rejected_by=rejected_by.cast(VALIDATION_SCHEMA["rejected_by"]))


# ==================================================================================================
#  count_rejections
# ==================================================================================================
def count_rejections(output: pl.DataFrame) -> dict[RejectionReason, int]:
    """Return the number of rejected candidates per `RejectionReason` in a stage's output.

    An output without a ``rejected_by`` column rejects no candidate, so its count is empty.
    """
    if "rejected_by" not in output.columns:
        return {}
    else:
        rejected = output.filter(pl.col("rejected_by") != "")
        return {RejectionReason(reason): count for reason, count in rejected.group_by("rejected_by").len().iter_rows()}
