"""`PipelineStage` is the base class of a benchmark suite pipeline stage; `PipelineStageOutput` is what it returns."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

import polars as pl

from sunnbear._core.problems.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool, WorkerTask


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
    def _run_per_formula[C, R](
        candidates: Sequence[C],
        *,
        problem_id: Callable[[C], str],
        build_task: Callable[[tuple[C, ...]], WorkerTask[list[R]]],
        worker_pool: WorkerPool,
    ) -> dict[str, R]:
        """Return each candidate's result from `build_task`, keyed by problem id, with every formula in 1 batch.

        Every candidate of a formula goes to the same task, so each formula is compiled in only 1 worker.
        """
        batches = worker_pool.split_into_batches(
            candidates, group_key=lambda candidate: ProblemId.from_string(problem_id(candidate)).formula_id
        )
        tasks = {batch_idx: build_task(tuple(batch)) for batch_idx, batch in enumerate(batches)}
        results_by_problem_id: dict[str, R] = {}
        for batch_idx, results in worker_pool.run(tasks):
            results_by_problem_id.update(zip(map(problem_id, batches[batch_idx]), results, strict=True))
        return results_by_problem_id


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
