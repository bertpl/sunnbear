"""Candidate validation, the second stage of the benchmark suite pipeline, records which check rejects each candidate.

The checks run in sequence, cheapest first, and a candidate is rejected by its first failed check. Rejected candidates
stay in the output, so that the reasons can be counted per formula.

The output holds every candidate of the candidate generation stage, with the columns of `CHECKED_CANDIDATES_SCHEMA`:
its ``rejected_by`` column names the check that rejected the candidate, as a `RejectionReason`, or holds ``""`` for a
valid candidate.

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

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage

from .s1_candidate_generation import CANDIDATES_SCHEMA

# A candidate whose bound-to-width ratio exceeds this limit is rejected by the bound-to-width ratio check.
MAX_BOUND_TO_WIDTH_RATIO = 100.0


# ==================================================================================================
#  RejectionReason
# ==================================================================================================
class RejectionReason(StrEnum):
    """A `RejectionReason` names the validation check that rejected a candidate."""

    BOUND_TO_WIDTH_RATIO = "bound_to_width_ratio"


CHECKED_CANDIDATES_SCHEMA: dict[str, pl.DataType] = {
    **CANDIDATES_SCHEMA,
    "rejected_by": pl.Enum(["", *RejectionReason]),
}


# ==================================================================================================
#  CandidateValidationStage
# ==================================================================================================
class CandidateValidationStage(PipelineStage):
    """`CandidateValidationStage` runs the validation checks, and records the check that rejected each candidate."""

    output_name = "s2_checked_candidates"

    def compute_output(self, previous_output: pl.DataFrame) -> pl.DataFrame:
        """Return the candidates with a ``rejected_by`` column: the check that rejected each, or ``""`` if none did.

        Args:
            previous_output: The output of candidate generation, with the columns of `CANDIDATES_SCHEMA`.
        """
        bound_to_width_ratio = pl.max_horizontal(pl.col("a").abs(), pl.col("b").abs()) / (pl.col("b") - pl.col("a"))
        # The reason goes in as its string value, because polars 1.0 turns a `RejectionReason` member into a literal of
        # an enum type whose only category is that member, and the ``otherwise`` value ``""`` cannot be cast to that
        # type.
        rejected_by = (
            pl.when(bound_to_width_ratio > MAX_BOUND_TO_WIDTH_RATIO)
            .then(pl.lit(RejectionReason.BOUND_TO_WIDTH_RATIO.value))
            .otherwise(pl.lit(""))
        )
        return previous_output.with_columns(rejected_by=rejected_by.cast(CHECKED_CANDIDATES_SCHEMA["rejected_by"]))
