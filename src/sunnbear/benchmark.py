"""This module re-exports the benchmark layer's public names: the shipped (u, v) tuple set and its construction.

What the tuple set is, and how it is constructed, is described in the docstrings of
`sunnbear._core.benchmark.tuple_set`.
"""

from ._core.benchmark import UV_TUPLES_SIZES, UvTuples, UvTuplesStats, generate_uv_tuples, uv_tuples

__all__ = ["UV_TUPLES_SIZES", "UvTuples", "UvTuplesStats", "generate_uv_tuples", "uv_tuples"]
