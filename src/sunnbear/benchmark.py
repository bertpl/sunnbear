"""This module re-exports the benchmark layer's public names: the shipped (u, v) tuple set and its construction.

`uv_tuples(size)` returns one size of the shipped set, `generate_uv_tuples` constructs an equivalent
set, and `UvTuples` holds either one.
"""

from ._core.benchmark import UV_TUPLES_SIZES, UvTuples, UvTuplesStats, generate_uv_tuples, uv_tuples

__all__ = ["UV_TUPLES_SIZES", "UvTuples", "UvTuplesStats", "generate_uv_tuples", "uv_tuples"]
