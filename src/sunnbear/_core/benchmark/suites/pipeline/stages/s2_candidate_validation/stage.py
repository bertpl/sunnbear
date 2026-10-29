"""`CandidateValidationStage` runs the validation checks on every candidate and keeps the candidates that pass them."""

import polars as pl

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import (
    PipelineStage,
    PipelineStageOutput,
    RejectionReason,
    build_output_with_rejection_reports,
)
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool

from .check1_bound_to_width_ratio import exceeds_max_bound_to_width_ratio
from .function_evaluating_checks_task import FunctionEvaluatingChecksTask

# The stage adds these columns to the valid candidates: their c-ranges.
C_RANGE_SCHEMA: dict[str, pl.DataType] = {"c_min": pl.Float64(), "c_max": pl.Float64()}


# ==================================================================================================
#  CandidateValidationStage
# ==================================================================================================
class CandidateValidationStage(PipelineStage):
    """`CandidateValidationStage` keeps the candidates that pass every check, and adds their c-ranges.

    It reports each rejected candidate with its `RejectionReason`, and the counts of the rejections per formula.
    """

    output_name = "s2_valid_candidates"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the valid candidates with their c-ranges, and the reports on the rejected candidates.

        The checks run in order, and each runs only on the candidates that passed the checks before it.

        The checks that evaluate f run in `FunctionEvaluatingChecksTask` tasks on `worker_pool`; each task holds every
        candidate of its formulas, so each formula is compiled in only 1 worker.

        Args:
            previous_table: The output table of candidate generation, with the columns ``problem_id``, ``a`` and
                ``b``.
            worker_pool: The worker pool of the run, in which the checks that evaluate f run.

        Returns:
            The stage's output, as `build_output_with_rejection_reports` describes it, whose table holds the columns
            of `previous_table` and of `C_RANGE_SCHEMA`.
        """
        # --- the bound-to-width ratio check -----
        is_ratio_too_large = previous_table.select(exceeds_max_bound_to_width_ratio()).to_series()
        ratio_rejected_problem_ids = previous_table.filter(is_ratio_too_large)["problem_id"]
        results_by_problem_id: dict[str, CRange | RejectionReason] = dict.fromkeys(
            ratio_rejected_problem_ids, RejectionReason.BOUND_TO_WIDTH_RATIO
        )

        # --- the checks that evaluate f ---------
        problem_ids_to_evaluate = previous_table.filter(~is_ratio_too_large)["problem_id"].to_list()
        batches = worker_pool.split_into_batches(
            problem_ids_to_evaluate, group_key=lambda problem_id: ProblemId.from_string(problem_id).formula_id
        )
        tasks = {
            batch_idx: FunctionEvaluatingChecksTask(problem_ids=tuple(batch)) for batch_idx, batch in enumerate(batches)
        }
        for batch_idx, results in worker_pool.run(tasks):
            results_by_problem_id.update(zip(batches[batch_idx], results, strict=True))

        # --- 1 row per candidate ----------------
        results = [results_by_problem_id[problem_id] for problem_id in previous_table["problem_id"]]
        c_mins = [result.c_min if isinstance(result, CRange) else None for result in results]
        c_maxs = [result.c_max if isinstance(result, CRange) else None for result in results]
        table = previous_table.with_columns(
            pl.Series("c_min", c_mins, dtype=C_RANGE_SCHEMA["c_min"]),
            pl.Series("c_max", c_maxs, dtype=C_RANGE_SCHEMA["c_max"]),
        )
        return build_output_with_rejection_reports(
            table,
            [result if isinstance(result, RejectionReason) else None for result in results],
            added_columns=C_RANGE_SCHEMA,
        )
