"""Validation, the second stage of the suite pipeline, runs the validation checks on every candidate.

The checks run in sequence, cheapest first, and a candidate is rejected by the first check that it fails.
Rejected candidates stay in the output, so that the reasons can be counted per formula.

The output holds every candidate of the candidate generation stage, with the columns of
`VALIDATED_CANDIDATES_SCHEMA`: its ``rejected_by`` column names the check that rejected the candidate,
as a `RejectionReason`, or holds ``""`` for a valid candidate.

The interval check, the first check, rejects a candidate whose interval lies far from 0 relative to its
width: its ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds `MAX_INTERVAL_RATIO`.

Rounding a bound changes the interval's width by up to about ``eps * max(abs(a), abs(b))``, a share of
the width that grows with the ratio. At a tolerance close to one where bisection's evaluation count
steps by 1, that change can move the count across the step, so a larger ratio puts more tolerances at
risk. The limit is stricter than the one that `compute_xtol_range` applies to users' own functions at
the default `n_bisection_fevals`.
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


VALIDATED_CANDIDATES_SCHEMA: dict[str, pl.DataType] = {
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
    return candidates.with_columns(rejected_by=rejected_by.cast(VALIDATED_CANDIDATES_SCHEMA["rejected_by"]))
