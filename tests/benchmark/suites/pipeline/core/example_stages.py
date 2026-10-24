"""This module defines small stages for the tests of the pipeline framework, so those tests need no formulas.

The first 3 stages follow the rules of the chain, and the third runs its work as tasks in the run's worker pool; each
of the others breaks 1 rule.
"""

from dataclasses import dataclass

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageOutput
from sunnbear._core.utils.worker_pool import WorkerPool


class ExampleNumbersStage(PipelineStage):
    """`ExampleNumbersStage` outputs the numbers 1, 2 and 3, with the ids ``n1``, ``n2`` and ``n3``."""

    output_name = "s1_numbers"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return a column ``x`` with the numbers 1, 2 and 3."""
        return PipelineStageOutput(table=pl.DataFrame({"function_id": ["n1", "n2", "n3"], "x": [1.0, 2.0, 3.0]}))


class ExampleSmallNumbersStage(PipelineStage):
    """`ExampleSmallNumbersStage` keeps the numbers up to 2, adds their doubles, and reports the dropped numbers."""

    output_name = "s2_small_numbers"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the numbers up to 2 with a column ``doubled_x``, and the report ``large_numbers``."""
        is_large = pl.col("x") > 2.0
        return PipelineStageOutput(
            table=previous_table.filter(~is_large).with_columns(doubled_x=2.0 * pl.col("x")),
            reports={"large_numbers": previous_table.filter(is_large)},
        )


@dataclass(frozen=True)
class ExampleSquaringTask:
    """`ExampleSquaringTask` squares numbers, in a worker process or in this process."""

    xs: tuple[float, ...]

    def run(self) -> list[float]:
        """Return the square of each number, in order."""
        return [x * x for x in self.xs]


class ExampleSquaresStage(PipelineStage):
    """`ExampleSquaresStage` adds the squares of the numbers, which tasks in the run's worker pool compute."""

    output_name = "s2_squares"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return `previous_table` with a column ``squared_x``, from tasks that each square the numbers of 1 batch."""
        batches = worker_pool.split_into_batches(previous_table.rows(named=True), key=lambda row: int(row["x"]))
        tasks = {
            batch_idx: ExampleSquaringTask(xs=tuple(row["x"] for row in batch))
            for batch_idx, batch in enumerate(batches)
        }
        squares_by_function_id: dict[str, float] = {}
        for batch_idx, squares in worker_pool.run(tasks):
            function_ids = [row["function_id"] for row in batches[batch_idx]]
            squares_by_function_id.update(zip(function_ids, squares, strict=True))
        squared_xs = [squares_by_function_id[function_id] for function_id in previous_table["function_id"]]
        return PipelineStageOutput(table=previous_table.with_columns(squared_x=pl.Series(squared_xs)))


class ExampleIdlessStage(PipelineStage):
    """`ExampleIdlessStage` breaks a rule of the chain: its output table has no ``function_id`` column."""

    output_name = "s1_idless"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return a column ``x`` only."""
        return PipelineStageOutput(table=pl.DataFrame({"x": [1.0]}))


class ExampleRowDuplicatingStage(PipelineStage):
    """`ExampleRowDuplicatingStage` breaks a rule of the chain: its output table holds every row twice."""

    output_name = "s2_duplicated_numbers"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return `previous_table` twice."""
        return PipelineStageOutput(table=pl.concat([previous_table, previous_table]))


class ExampleColumnDroppingStage(PipelineStage):
    """`ExampleColumnDroppingStage` breaks a rule of the chain: its output table drops the column ``x``."""

    output_name = "s2_ids"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the column ``function_id`` only."""
        return PipelineStageOutput(table=previous_table.select("function_id"))


class ExampleRowAddingStage(PipelineStage):
    """`ExampleRowAddingStage` breaks a rule of the chain: its output table adds the number 4, as ``n4``."""

    output_name = "s2_more_numbers"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return `previous_table` with 1 more row."""
        return PipelineStageOutput(table=pl.concat([previous_table, pl.DataFrame({"function_id": ["n4"], "x": [4.0]})]))
