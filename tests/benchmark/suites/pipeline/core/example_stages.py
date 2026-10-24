"""This module defines small stages for the tests of the pipeline framework, so those tests need no formulas."""

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage


class ExampleNumbersStage(PipelineStage):
    """`ExampleNumbersStage` outputs the numbers 1, 2 and 3."""

    output_name = "s1_numbers"

    def compute_output(self, previous_output: pl.DataFrame) -> pl.DataFrame:
        """Return a column ``x`` with the numbers 1, 2 and 3."""
        return pl.DataFrame({"x": [1.0, 2.0, 3.0]})


class ExampleCheckedNumbersStage(PipelineStage):
    """`ExampleCheckedNumbersStage` rejects the numbers above 2, as ``too_large``."""

    output_name = "s2_checked_numbers"

    def compute_output(self, previous_output: pl.DataFrame) -> pl.DataFrame:
        """Return the numbers with a ``rejected_by`` column."""
        return previous_output.with_columns(
            rejected_by=pl.when(pl.col("x") > 2.0).then(pl.lit("too_large")).otherwise(pl.lit(""))
        )


class ExampleColumnDroppingStage(PipelineStage):
    """`ExampleColumnDroppingStage` breaks the chain's rule: its output drops the column ``x`` of its input."""

    output_name = "s2_doubled_numbers"

    def compute_output(self, previous_output: pl.DataFrame) -> pl.DataFrame:
        """Return the doubled numbers, without the column ``x``."""
        return previous_output.select(doubled_x=2.0 * pl.col("x"))
