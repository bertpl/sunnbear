"""This module holds helpers for functions that accept both eager and lazy polars frames."""

import polars as pl


def collect_if_eager(frame: pl.DataFrame | pl.LazyFrame, result: pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame:
    """Return `result` collected when `frame` is an eager frame, else `result` as it is."""
    if isinstance(frame, pl.DataFrame):
        return result.collect()
    else:
        return result
