"""Candidate generation, the first stage of the benchmark suite pipeline, builds every candidate of every formula.

A candidate is 1 test problem that a formula builds for 1 tuple of its parameters, on its interval ``[a, b]``.

The stage adds the candidates formula by formula, in the given order, and within a formula in the order of
`Formula.build_all_candidates`, with their interval bounds. `FormulaRegistry.candidate_from_id` rebuilds a candidate
from its id, so the state holds nothing more.
"""

from collections.abc import Sequence

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.state import CandidateGenerationStateAccessor, IntervalBounds
from sunnbear._core.problems.core import Formula
from sunnbear._core.utils.worker_pool import WorkerPool


# ==================================================================================================
#  CandidateGenerationStage
# ==================================================================================================
class CandidateGenerationStage(PipelineStage[CandidateGenerationStateAccessor]):
    """`CandidateGenerationStage` adds every candidate of every given formula, with its interval bounds."""

    stage_id = PipelineStageId.CANDIDATE_GENERATION

    def __init__(self, formulas: Sequence[Formula]) -> None:
        """Create the stage for `formulas`, the corpus of the pipeline run."""
        self.formulas = formulas

    def run(self, state_accessor: CandidateGenerationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Add every candidate of every formula.

        Raises:
            ValueError: If a formula fails the checks of `Formula.build_all_candidates`.
        """
        state_accessor.add_candidates(
            {
                candidate.id: IntervalBounds(a=candidate.a, b=candidate.b)
                for formula in self.formulas
                for candidate in formula.build_all_candidates()
            }
        )
