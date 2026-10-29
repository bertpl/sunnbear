"""`CandidateCharacterizationStage` is the base class of the stages that compute the candidates' feature vectors."""

from collections.abc import Sequence
from typing import ClassVar

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import (
    PipelineStage,
    PipelineStageOutput,
    RejectionReason,
    build_output_with_rejection_reports,
)
from sunnbear._core.problems.core import ProblemId
from sunnbear._core.solvers.core import SolverConfig
from sunnbear._core.utils.worker_pool import WorkerPool

from .characterization_task import CandidateCharacterizationTask
from .fidelity import FeatureFidelity


# ==================================================================================================
#  CandidateCharacterizationStage
# ==================================================================================================
class CandidateCharacterizationStage(PipelineStage):
    """`CandidateCharacterizationStage` adds each candidate's feature vector, and rejects the candidates that fail.

    A child class is 1 stage of the pipeline: it sets `output_name` and `fidelity`, the only things in which the
    characterization stages differ.

    A candidate is rejected when 1 of its solves ends with `SolveStatus.FUNCTION_ERROR`, or when snuffled's diagnostics
    reject it at 1 of its analyses, by the rules that validation's snuffled diagnostics check applies too.

    Class attributes:
        fidelity: The fidelity of the feature vectors, which sets the tuples of the solves and of snuffled's analyses,
            the budget of the analyses, and the names of the feature columns.
    """

    fidelity: ClassVar[FeatureFidelity]

    def __init__(self, core_solver_configs: Sequence[SolverConfig]) -> None:
        """Create the stage, whose empirical block holds the solves of `core_solver_configs`.

        For the benchmark suites, the configs are those whose role characterizes test problems
        (`SolverRole.is_used_for_problem_characterization`).

        Raises:
            ValueError: If `core_solver_configs` is empty.
        """
        if not core_solver_configs:
            raise ValueError("A characterization stage needs at least 1 core solver config.")
        else:
            self.solver_ids = tuple(config.solver_id for config in core_solver_configs)

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the kept candidates with their feature vectors, and the reports on the rejected candidates.

        The candidates are characterized in `CandidateCharacterizationTask` tasks on `worker_pool`; each task holds
        every candidate of its formulas, so each formula is compiled in only 1 worker.

        Args:
            previous_table: The output table of the stage before, with the columns ``problem_id``, ``c_min`` and
                ``c_max``.
            worker_pool: The worker pool of the run, in which the candidates are characterized.

        Returns:
            The stage's output, as `build_output_with_rejection_reports` describes it, whose table adds the columns of
            `FeatureFidelity.feature_column_names`, of type `pl.Float64`, to those of `previous_table`.
        """
        # --- characterize, in the worker pool ---
        candidates = previous_table.select("problem_id", "c_min", "c_max").rows()
        batches = worker_pool.split_into_batches(
            candidates, group_key=lambda candidate: ProblemId.from_string(candidate[0]).formula_id
        )
        tasks = {
            batch_idx: CandidateCharacterizationTask(
                candidates=tuple(batch), solver_ids=self.solver_ids, fidelity=self.fidelity
            )
            for batch_idx, batch in enumerate(batches)
        }
        results_by_problem_id: dict[str, dict[str, float] | RejectionReason] = {}
        for batch_idx, results in worker_pool.run(tasks):
            batch_problem_ids = [problem_id for problem_id, _, _ in batches[batch_idx]]
            results_by_problem_id.update(zip(batch_problem_ids, results, strict=True))

        # --- 1 row per candidate ----------------
        results = [results_by_problem_id[problem_id] for problem_id in previous_table["problem_id"]]
        column_names = self.fidelity.feature_column_names(self.solver_ids)
        table = previous_table.with_columns(
            pl.Series(
                column_name,
                [None if isinstance(result, RejectionReason) else result[column_name] for result in results],
                dtype=pl.Float64(),
            )
            for column_name in column_names
        )
        return build_output_with_rejection_reports(
            table,
            [result if isinstance(result, RejectionReason) else None for result in results],
            added_columns=column_names,
        )
