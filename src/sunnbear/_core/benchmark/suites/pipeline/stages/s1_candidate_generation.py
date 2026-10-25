"""Candidate generation, the first stage of the benchmark suite pipeline, builds every candidate of every formula.

A candidate is 1 test problem that a formula builds for 1 tuple of its parameters, on its interval ``[a, b]``.

Its output holds 1 row per candidate, with the columns of `CANDIDATES_SCHEMA`. The rows run formula by formula, in
the given order, and within a formula in the order of `Formula.build_all_candidates`.

The output holds only the id and the interval bounds, because `FormulaRegistry.candidate_from_id` rebuilds a
candidate from its ``problem_id``.
"""

from collections.abc import Sequence

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageOutput
from sunnbear._core.problems.core import Formula
from sunnbear._core.utils.worker_pool import WorkerPool

CANDIDATES_SCHEMA: dict[str, pl.DataType] = {
    "problem_id": pl.String(),
    "a": pl.Float64(),
    "b": pl.Float64(),
}


# ==================================================================================================
#  CandidateGenerationStage
# ==================================================================================================
class CandidateGenerationStage(PipelineStage):
    """`CandidateGenerationStage` lists every candidate of every given formula, with its id and interval bounds."""

    output_name = "s1_candidates"

    def __init__(self, formulas: Sequence[Formula]) -> None:
        """Create the stage for `formulas`, the corpus of the pipeline run."""
        self.formulas = formulas

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return every candidate of every formula: its id and its interval bounds ``a`` and ``b``.

        As the first stage, it receives an empty `previous_table`.

        Raises:
            ValueError: If a formula fails the checks of `Formula.build_all_candidates`.
        """
        candidates = [candidate for formula in self.formulas for candidate in formula.build_all_candidates()]
        table = pl.DataFrame(
            {
                "problem_id": [str(candidate.id) for candidate in candidates],
                "a": [candidate.a for candidate in candidates],
                "b": [candidate.b for candidate in candidates],
            },
            schema=CANDIDATES_SCHEMA,
        )
        return PipelineStageOutput(table=table)
