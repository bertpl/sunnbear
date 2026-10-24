"""Candidate validation, the second stage of the benchmark suite pipeline, runs the validation checks.

The checks run in sequence, cheapest first, and a candidate is rejected by its first failed check. Rejected candidates
stay in the output, so that the reasons can be counted per formula.

The output holds every candidate of the candidate generation stage, with the columns of `CHECKED_CANDIDATES_SCHEMA`:
its ``rejected_by`` column names the check that rejected the candidate, as a `RejectionReason`, or holds ``""`` for a
valid candidate.

The interval check, the first check, rejects a candidate whose interval lies far from 0 relative to its width: its
bound-to-width ratio ``max(abs(a), abs(b)) / (b - a)`` exceeds `MAX_BOUND_TO_WIDTH_RATIO`.

Rounding a bound changes the interval's width by up to about ``eps * max(abs(a), abs(b))``, with ``eps`` the float64
machine epsilon; relative to the width, that change is about ``eps`` times the ratio.

Bisection's evaluation count changes by 1 wherever ``(b - a) / (2*xtol)`` crosses a power of 2, so for an ``xtol``
close to such a value, the change in width can shift the count by 1. A larger ratio widens the range of ``xtol``
values at which the count depends on rounding.

The limit is stricter than `compute_xtol_range`'s limit for users' own functions at the default
`n_bisection_fevals`.
"""

from collections.abc import Mapping
from enum import StrEnum

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage

from .s1_candidate_generation import CANDIDATES_SCHEMA, CandidateGeneration

# A candidate whose bound-to-width ratio exceeds this limit is rejected by the interval check.
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
#  CandidateValidation
# ==================================================================================================
class CandidateValidation(PipelineStage):
    """`CandidateValidation` runs the validation checks on every candidate, and records the check that rejected it."""

    output_name = "s2_checked_candidates"
    input_stages = (CandidateGeneration,)

    def compute_output(self, inputs: Mapping[type[PipelineStage], pl.DataFrame]) -> pl.DataFrame:
        """Return the candidates with a ``rejected_by`` column: the check that rejected each, or ``""`` if none did."""
        candidates = inputs[CandidateGeneration]
        bound_to_width_ratio = pl.max_horizontal(pl.col("a").abs(), pl.col("b").abs()) / (pl.col("b") - pl.col("a"))
        # The reason goes in as its string value: polars 1.0 turns an `Enum` member into a literal of an enum type with
        # that 1 category, to which ``""`` then fails to convert.
        rejected_by = (
            pl.when(bound_to_width_ratio > MAX_BOUND_TO_WIDTH_RATIO)
            .then(pl.lit(RejectionReason.BOUND_TO_WIDTH_RATIO.value))
            .otherwise(pl.lit(""))
        )
        return candidates.with_columns(rejected_by=rejected_by.cast(CHECKED_CANDIDATES_SCHEMA["rejected_by"]))
