"""This module defines small stages for the tests of the pipeline framework, so those tests need no formulas.

The first 2 stages follow the rules of the chain; each of the others breaks 1 rule.
"""

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageOutput


class ExampleNumbersStage(PipelineStage):
    """`ExampleNumbersStage` outputs the numbers 1, 2 and 3, with the ids ``n1``, ``n2`` and ``n3``."""

    output_name = "s1_numbers"

    def compute_output(self, previous_table: pl.DataFrame) -> PipelineStageOutput:
        """Return a column ``x`` with the numbers 1, 2 and 3."""
        return PipelineStageOutput(table=pl.DataFrame({"function_id": ["n1", "n2", "n3"], "x": [1.0, 2.0, 3.0]}))


class ExampleSmallNumbersStage(PipelineStage):
    """`ExampleSmallNumbersStage` keeps the numbers up to 2, adds their doubles, and reports the dropped numbers."""

    output_name = "s2_small_numbers"

    def compute_output(self, previous_table: pl.DataFrame) -> PipelineStageOutput:
        """Return the numbers up to 2 with a column ``doubled_x``, and the report ``large_numbers``."""
        is_large = pl.col("x") > 2.0
        return PipelineStageOutput(
            table=previous_table.filter(~is_large).with_columns(doubled_x=2.0 * pl.col("x")),
            reports={"large_numbers": previous_table.filter(is_large)},
        )


class ExampleIdlessStage(PipelineStage):
    """`ExampleIdlessStage` breaks a rule of the chain: its output table has no ``function_id`` column."""

    output_name = "s1_idless"

    def compute_output(self, previous_table: pl.DataFrame) -> PipelineStageOutput:
        """Return a column ``x`` only."""
        return PipelineStageOutput(table=pl.DataFrame({"x": [1.0]}))


class ExampleRowDuplicatingStage(PipelineStage):
    """`ExampleRowDuplicatingStage` breaks a rule of the chain: its output table holds every row twice."""

    output_name = "s2_duplicated_numbers"

    def compute_output(self, previous_table: pl.DataFrame) -> PipelineStageOutput:
        """Return `previous_table` twice."""
        return PipelineStageOutput(table=pl.concat([previous_table, previous_table]))


class ExampleColumnDroppingStage(PipelineStage):
    """`ExampleColumnDroppingStage` breaks a rule of the chain: its output table drops the column ``x``."""

    output_name = "s2_ids"

    def compute_output(self, previous_table: pl.DataFrame) -> PipelineStageOutput:
        """Return the column ``function_id`` only."""
        return PipelineStageOutput(table=previous_table.select("function_id"))


class ExampleRowAddingStage(PipelineStage):
    """`ExampleRowAddingStage` breaks a rule of the chain: its output table adds the number 4, as ``n4``."""

    output_name = "s2_more_numbers"

    def compute_output(self, previous_table: pl.DataFrame) -> PipelineStageOutput:
        """Return `previous_table` with 1 more row."""
        return PipelineStageOutput(table=pl.concat([previous_table, pl.DataFrame({"function_id": ["n4"], "x": [4.0]})]))
