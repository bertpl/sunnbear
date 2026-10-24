"""Candidate generation, the first stage of the benchmark suite pipeline, builds every candidate of every formula.

Its output holds 1 row per candidate, with the columns of `CANDIDATES_SCHEMA`. The rows run formula by formula, in
the given order, and within a formula in the order of `Formula.build_all_candidates`. The output holds only the id
and the interval bounds, because `FormulaRegistry.candidate_from_id` rebuilds a candidate from its ``function_id``.
"""

from collections.abc import Mapping, Sequence

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage
from sunnbear._core.functions.core import Formula

CANDIDATES_SCHEMA: dict[str, pl.DataType] = {
    "function_id": pl.String(),
    "a": pl.Float64(),
    "b": pl.Float64(),
}


# ==================================================================================================
#  CandidateGeneration
# ==================================================================================================
class CandidateGeneration(PipelineStage):
    """`CandidateGeneration` lists every candidate of every formula of the corpus, with its id and interval bounds."""

    output_name = "s1_candidates"

    def __init__(self, formulas: Sequence[Formula]) -> None:
        """Generate the candidates of `formulas`, the corpus of the pipeline run."""
        self.formulas = formulas

    def compute_output(self, inputs: Mapping[type[PipelineStage], pl.DataFrame]) -> pl.DataFrame:
        """Return every candidate of every formula: its id and its interval bounds ``a`` and ``b``.

        Raises:
            ValueError: If a formula fails the checks of `Formula.build_all_candidates`.
        """
        candidates = [candidate for formula in self.formulas for candidate in formula.build_all_candidates()]
        return pl.DataFrame(
            {
                "function_id": [str(candidate.id) for candidate in candidates],
                "a": [candidate.a for candidate in candidates],
                "b": [candidate.b for candidate in candidates],
            },
            schema=CANDIDATES_SCHEMA,
        )
