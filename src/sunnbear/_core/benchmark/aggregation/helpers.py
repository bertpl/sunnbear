"""Helpers that the aggregation functions share."""

import polars as pl


def collect_if_eager(frame: pl.DataFrame | pl.LazyFrame, result: pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame:
    """Return `result` collected when `frame` is an eager frame, else `result` as it is.

    An aggregation function builds its result as a lazy query on `frame.lazy()`, and returns it with this
    function, so that it returns the same kind of frame that it was given.
    """
    if isinstance(frame, pl.DataFrame):
        return result.collect()
    else:
        return result
