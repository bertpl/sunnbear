"""`CandidateValidationStage` runs the validation checks on every candidate and keeps the candidates that pass them."""

from typing import TYPE_CHECKING

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.state import CandidateValidationStateAccessor
from sunnbear._core.utils.worker_pool import WorkerPool

from .check1_bound_to_width_ratio import exceeds_max_bound_to_width_ratio
from .function_evaluating_checks_task import FunctionEvaluatingChecksTask

if TYPE_CHECKING:
    from sunnbear._core.benchmark.protocol import CRange
    from sunnbear._core.problems.core import ProblemId


# ==================================================================================================
#  CandidateValidationStage
# ==================================================================================================
class CandidateValidationStage(PipelineStage[CandidateValidationStateAccessor]):
    """`CandidateValidationStage` rejects the candidates that fail a check, and stores the c-ranges of the others."""

    stage_id = PipelineStageId.CANDIDATE_VALIDATION

    def run(self, state_accessor: CandidateValidationStateAccessor, *, worker_pool: WorkerPool) -> None:
        """Reject each candidate at its first failed check, then store the c-range of each candidate that passes.

        The checks run in order, and each runs only on the candidates that passed the checks before it. The checks
        that evaluate f run in `FunctionEvaluatingChecksTask` tasks on `worker_pool`.
        """
        # --- the bound-to-width ratio check -----
        interval_bounds = state_accessor.interval_bounds()
        results_by_problem_id: dict[ProblemId, CRange | str] = {
            problem_id: "bound_to_width_ratio"
            for problem_id, bounds in interval_bounds.items()
            if exceeds_max_bound_to_width_ratio(bounds.a, bounds.b)
        }

        # --- the checks that evaluate f ---------
        results_by_problem_id.update(
            self._run_in_formula_batches(
                [problem_id for problem_id in interval_bounds if problem_id not in results_by_problem_id],
                problem_id_key=lambda problem_id: problem_id,
                build_task=lambda batch: FunctionEvaluatingChecksTask(problem_ids=batch),
                worker_pool=worker_pool,
            )
        )

        # --- rejections and c-ranges ------------
        c_ranges: dict[ProblemId, CRange] = {}
        for problem_id in interval_bounds:
            result = results_by_problem_id[problem_id]
            if isinstance(result, str):
                state_accessor.reject(problem_id, result)
            else:
                c_ranges[problem_id] = result
        state_accessor.set_c_ranges(c_ranges)
