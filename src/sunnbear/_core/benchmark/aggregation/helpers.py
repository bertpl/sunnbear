"""The aggregation functions share these helpers."""

import polars as pl

from sunnbear._core.solvers.core import SolveStatus


def is_converged_expression() -> pl.Expr:
    """Return an expression that is true for a solve that converged, whether its answer is correct or not."""
    return pl.col("status") == SolveStatus.CONVERGED.value


def collect_if_eager(frame: pl.DataFrame | pl.LazyFrame, result: pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame:
    """Return `result` collected when `frame` is an eager frame, else `result` as it is.

    An aggregation function builds its result as a lazy query on `frame.lazy()` and returns it through
    `collect_if_eager`, so that the aggregation function returns the same kind of frame that it was given.
    """
    if isinstance(frame, pl.DataFrame):
        return result.collect()
    else:
        return result
