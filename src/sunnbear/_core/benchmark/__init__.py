"""This package holds the benchmark layer: the (u, v) tuple set that drives every Monte Carlo benchmark run.

Importing it registers the `uv_tuples` artifact declaration with `ArtifactRegistry`.
"""

from .tuple_set import UV_TUPLES_SIZES, UvTuples, UvTuplesStats, generate_uv_tuples, uv_tuples

__all__ = ["UV_TUPLES_SIZES", "UvTuples", "UvTuplesStats", "generate_uv_tuples", "uv_tuples"]
