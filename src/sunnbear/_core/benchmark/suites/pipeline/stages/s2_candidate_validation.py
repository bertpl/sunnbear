"""Candidate validation, the second stage of the benchmark suite pipeline, keeps the candidates that pass every check.

The checks run in sequence, cheapest first, and a candidate is rejected by its first failed check. The output table
holds the valid candidates, with the columns of `CANDIDATES_SCHEMA`. The report ``rejected_candidates`` holds the
rejected candidates, with the columns of `REJECTED_CANDIDATES_SCHEMA`: the same columns, and ``rejected_by``, the
`RejectionReason` of the check that rejected the candidate.

The bound-to-width ratio check, the first check, rejects a candidate whose interval lies far from 0 relative to its
width: its bound-to-width ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds `MAX_BOUND_TO_WIDTH_RATIO`.

Rounding a bound to float64, as bisection does when a midpoint becomes a new bound, changes the interval's width by up
to about ``eps * max(abs(a), abs(b))``, with ``eps`` the float64 machine epsilon; relative to the width, that change is
about ``eps`` times the bound-to-width ratio.

Bisection's evaluation count changes by 1 wherever ``(b - a) / (2*xtol)`` crosses a power of 2, so for an ``xtol`` at
which that quotient is close to a power of 2, the change in width can shift the count by 1. A larger bound-to-width
ratio widens the range of ``xtol`` values at which the count depends on rounding.

`MAX_BOUND_TO_WIDTH_RATIO` is stricter than the largest bound-to-width ratio that `compute_xtol_range` accepts for
users' own functions at the default `n_bisection_fevals`.
"""

from enum import StrEnum

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageOutput

from .s1_candidate_generation import CANDIDATES_SCHEMA

# A candidate whose bound-to-width ratio exceeds this limit is rejected by the bound-to-width ratio check.
MAX_BOUND_TO_WIDTH_RATIO = 100.0


# ==================================================================================================
#  RejectionReason
# ==================================================================================================
class RejectionReason(StrEnum):
    """A `RejectionReason` names the validation check that rejected a candidate."""

    BOUND_TO_WIDTH_RATIO = "bound_to_width_ratio"


REJECTED_CANDIDATES_SCHEMA: dict[str, pl.DataType] = {
    **CANDIDATES_SCHEMA,
    "rejected_by": pl.Enum([reason.value for reason in RejectionReason]),
}


# ==================================================================================================
#  CandidateValidationStage
# ==================================================================================================
class CandidateValidationStage(PipelineStage):
    """`CandidateValidationStage` keeps the candidates that pass every check, and reports the others with a reason."""

    output_name = "s2_valid_candidates"

    def compute_output(self, previous_table: pl.DataFrame) -> PipelineStageOutput:
        """Return the valid candidates, and the report ``rejected_candidates`` of the others.

        Args:
            previous_table: The output table of candidate generation, with the columns of `CANDIDATES_SCHEMA`.
        """
        bound_to_width_ratio = pl.max_horizontal(pl.col("a").abs(), pl.col("b").abs()) / (pl.col("b") - pl.col("a"))
        is_rejected = bound_to_width_ratio > MAX_BOUND_TO_WIDTH_RATIO
        # The reason goes in as its string value: polars 1.0 turns a `RejectionReason` member into a literal of an enum
        # type whose only category is that member, which does not combine with other reasons in 1 column.
        rejected_by = pl.lit(RejectionReason.BOUND_TO_WIDTH_RATIO.value).cast(REJECTED_CANDIDATES_SCHEMA["rejected_by"])
        return PipelineStageOutput(
            table=previous_table.filter(~is_rejected),
            reports={"rejected_candidates": previous_table.filter(is_rejected).with_columns(rejected_by=rejected_by)},
        )
