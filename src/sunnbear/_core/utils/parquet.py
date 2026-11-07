"""`parquet_file_content` converts table columns to the content of a Parquet file."""

import io
from typing import Any

import polars as pl


def parquet_file_content(columns: dict[str, list[Any]]) -> bytes:
    """Return `columns`, each column name mapped to its values, as the content of a Parquet file."""
    buffer = io.BytesIO()
    pl.DataFrame(columns).write_parquet(buffer)
    return buffer.getvalue()
