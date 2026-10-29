"""`CandidateCharacterizationStage` is the base class of the stages that compute the candidates' feature vectors."""

import dataclasses
from collections.abc import Sequence
from typing import ClassVar

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import (
    PipelineStage,
    PipelineStageOutput,
    RejectionReason,
)
from sunnbear._core.solvers.core import SolverConfig
from sunnbear._core.utils.worker_pool import WorkerPool

from .characterization_task import CandidateCharacterizationTask
from .fidelity import FeatureFidelity


# ==================================================================================================
#  CandidateCharacterizationStage
# ==================================================================================================
class CandidateCharacterizationStage(PipelineStage):
    """`CandidateCharacterizationStage` adds feature vectors, and rejects candidates whose solves or analyses fail.

    The stage also adds the scale of each block of the features, as `FeatureFidelity.add_feature_scales` computes it.
    A stage reads only the output table of the stage before it, so the scales are stored in this stage's output
    table, where the next stage can read them, with the same value in every row.

    A child class is 1 stage of the pipeline: it sets `output_name` and `fidelity`, the only things in which the
    characterization stages differ.

    A candidate is rejected when 1 of its solves ends with `SolveStatus.FUNCTION_ERROR`, or when snuffled's diagnostics
    reject it at 1 of its analyses, by the rules of `extract_properties_or_rejection_reason`.

    Class attributes:
        fidelity: The `FeatureFidelity` of the feature vectors.
    """

    fidelity: ClassVar[FeatureFidelity]

    def __init__(self, core_solver_configs: Sequence[SolverConfig]) -> None:
        """Create the stage, which solves each candidate with `core_solver_configs`.

        Raises:
            ValueError: If `core_solver_configs` is empty.
        """
        if not core_solver_configs:
            raise ValueError("A characterization stage needs at least 1 core solver config.")
        else:
            self.solver_ids = tuple(config.solver_id for config in core_solver_configs)

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the kept candidates with their feature vectors, and the reports on the rejected candidates.

        The candidates are characterized in `CandidateCharacterizationTask` tasks on `worker_pool`, by
        `_run_in_formula_batches`.

        Args:
            previous_table: The output table of the stage before, with the columns ``problem_id``, ``c_min`` and
                ``c_max``.
            worker_pool: The worker pool of the run, in which the candidates are characterized.

        Returns:
            The stage's output, as `_build_output_with_rejection_reports` describes it. Its table holds these
            columns; every added column has type `pl.Float64`:

            - the columns of `previous_table`;
            - the columns of `FeatureFidelity.feature_column_names`;
            - the columns of `FeatureFidelity.feature_scale_column_names`, each holding, in every row, the scale that
              `FeatureFidelity.add_feature_scales` computes, or null when fewer than 2 candidates are kept.
        """
        # --- characterize, in the worker pool ---
        results_by_problem_id = self._run_in_formula_batches(
            previous_table.select("problem_id", "c_min", "c_max").rows(),
            problem_id_key=lambda candidate: candidate[0],
            build_task=lambda batch: CandidateCharacterizationTask(
                candidates=batch, solver_ids=self.solver_ids, fidelity=self.fidelity
            ),
            worker_pool=worker_pool,
        )

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
        output = self._build_output_with_rejection_reports(table, results, added_columns=column_names)
        return dataclasses.replace(output, table=self.fidelity.add_feature_scales(output.table))
