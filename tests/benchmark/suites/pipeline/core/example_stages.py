"""This module defines 2 small stages for the tests of the pipeline framework, so those tests need no formulas."""

from collections.abc import Mapping

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage


class ExampleNumbers(PipelineStage):
    """`ExampleNumbers` outputs the numbers 1, 2 and 3."""

    output_name = "s1_numbers"

    def compute_output(self, inputs: Mapping[type[PipelineStage], pl.DataFrame]) -> pl.DataFrame:
        """Return a column ``x`` with the numbers 1, 2 and 3."""
        return pl.DataFrame({"x": [1.0, 2.0, 3.0]})


class ExampleCheckedNumbers(PipelineStage):
    """`ExampleCheckedNumbers` rejects the numbers of `ExampleNumbers` above 2, as ``too_large``."""

    output_name = "s2_checked_numbers"
    input_stages = (ExampleNumbers,)

    def compute_output(self, inputs: Mapping[type[PipelineStage], pl.DataFrame]) -> pl.DataFrame:
        """Return the numbers with a ``rejected_by`` column."""
        return inputs[ExampleNumbers].with_columns(
            rejected_by=pl.when(pl.col("x") > 2.0).then(pl.lit("too_large")).otherwise(pl.lit(""))
        )
