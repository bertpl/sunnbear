"""`PipelineStage` is the base class of a benchmark suite pipeline stage; `PipelineStageOutput` is what it returns."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

import polars as pl

from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool, WorkerTask

from .rejections import (
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    REJECTIONS_PER_FORMULA_REPORT_NAME,
    RejectionReason,
)


# ==================================================================================================
#  PipelineStage
# ==================================================================================================
class PipelineStage(ABC):
    """A `PipelineStage` computes its output table from the output table of the stage before it.

    The stages form a chain of tables with 1 row per candidate, keyed by a ``problem_id`` column. The first stage
    creates the rows; each later stage keeps every column of its input and may add columns, and keeps a subset of
    the input's rows. So a stage finds everything that the stages before it computed in its input, and a candidate
    that a stage drops never reaches the stages after it. A stage can explain what it dropped in its reports.

    Class attributes:
        output_name: The name of the stage's output file in the `PipelineWorkspace`, without the suffix, e.g.
            ``s1_candidates``. It starts with ``s`` and the stage's position in the run order, so a listing of the
            workspace directory shows the outputs in run order.
    """

    output_name: ClassVar[str]

    @abstractmethod
    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> "PipelineStageOutput":
        """Return the stage's output table, which extends `previous_table`, and the stage's reports.

        Args:
            previous_table: The output table of the stage before this one; an empty table for the first stage.
            worker_pool: The worker pool of the run, in which the stage may run tasks. The stage's output must not
                depend on the pool's number of workers. The stage's tasks must be picklable `WorkerTask`s. A worker has
                imported the modules that define the run's formulas, and otherwise only what unpickling a task needs.
        """

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _run_in_formula_batches[C, R](
        candidates: Sequence[C],
        *,
        problem_id_key: Callable[[C], str],
        build_task: Callable[[tuple[C, ...]], WorkerTask[list[R]]],
        worker_pool: WorkerPool,
    ) -> dict[str, R]:
        """Return each candidate's result from `build_task`, keyed by problem id, with every formula in 1 batch.

        Every candidate of a formula goes to the same task, so each formula is compiled in only 1 worker.

        Args:
            candidates: The candidates to run, each with a distinct problem id.
            problem_id_key: Returns a candidate's problem id, as rendered by `ProblemId`.
            build_task: Builds the task of 1 batch, whose `run` returns 1 result per candidate of the batch, in the
                batch's order.
            worker_pool: The worker pool of the run, which splits the candidates into batches and runs their tasks.
        """
        batches = worker_pool.split_into_batches(
            candidates, group_key=lambda candidate: ProblemId.from_string(problem_id_key(candidate)).formula_id
        )
        tasks = {batch_idx: build_task(tuple(batch)) for batch_idx, batch in enumerate(batches)}
        results_by_problem_id: dict[str, R] = {}
        for batch_idx, results in worker_pool.run(tasks):
            results_by_problem_id.update(zip(map(problem_id_key, batches[batch_idx]), results, strict=True))
        return results_by_problem_id

    @staticmethod
    def _build_output_with_rejection_reports(
        table: pl.DataFrame, results: Sequence[object], *, added_columns: Collection[str]
    ) -> "PipelineStageOutput":
        """Return the output of a stage that rejects candidates, with its 2 reports on the rejected candidates.

        Args:
            table: Every row of the stage's input table, with the columns that the stage adds; on a rejected
                candidate's row, the added columns hold nulls.
            results: Each row's result in the stage, in the order of `table`: a `RejectionReason` for a candidate that
                the stage rejects, any other value for one that it keeps.
            added_columns: The names of the columns that the stage adds to its input table.

        Returns:
            The stage's output, which holds:

            - the output table: the rows of `table` whose result is not a `RejectionReason`;
            - the report `REJECTED_CANDIDATES_REPORT_NAME`: the other rows, without `added_columns`, and with the
              columns of `REJECTED_BY_SCHEMA`;
            - the report `REJECTIONS_PER_FORMULA_REPORT_NAME`: 1 row per formula, in the order of each formula's first
              row in `table`, with the columns ``formula_id``, ``n_candidates``, ``n_kept``, and 1 count per
              `RejectionReason`, named after its value.
        """
        table_with_reasons = table.with_columns(
            pl.Series(
                "rejected_by",
                [result.value if isinstance(result, RejectionReason) else None for result in results],
                dtype=REJECTED_BY_SCHEMA["rejected_by"],
            )
        )
        is_kept = pl.col("rejected_by").is_null()
        return PipelineStageOutput(
            table=table_with_reasons.filter(is_kept).drop(list(REJECTED_BY_SCHEMA)),
            reports={
                REJECTED_CANDIDATES_REPORT_NAME: table_with_reasons.filter(~is_kept).drop(list(added_columns)),
                REJECTIONS_PER_FORMULA_REPORT_NAME: PipelineStage._count_rejections_per_formula(table_with_reasons),
            },
        )

    @staticmethod
    def _count_rejections_per_formula(table: pl.DataFrame) -> pl.DataFrame:
        """Return the report `REJECTIONS_PER_FORMULA_REPORT_NAME` of `table`, which holds a ``rejected_by`` column."""
        formula_ids = [ProblemId.from_string(problem_id).formula_id for problem_id in table["problem_id"]]
        return (
            table.with_columns(formula_id=pl.Series(formula_ids, dtype=pl.String()))
            .group_by("formula_id", maintain_order=True)
            .agg(
                n_candidates=pl.len(),
                n_kept=pl.col("rejected_by").is_null().sum(),
                **{reason.value: (pl.col("rejected_by") == reason.value).sum() for reason in RejectionReason},
            )
        )


# ==================================================================================================
#  PipelineStageOutput
# ==================================================================================================
@dataclass(frozen=True)
class PipelineStageOutput:
    """A `PipelineStageOutput` holds what 1 stage computed: the table that the next stage reads, and its reports.

    Attributes:
        table: The stage's output table, which the next stage receives.
        reports: Tables that the next stage does not read, keyed by a name of the stage's choice, such as the
            candidates that the stage dropped and why; empty for a stage that reports nothing.
    """

    table: pl.DataFrame
    reports: Mapping[str, pl.DataFrame] = field(default_factory=dict)
