"""This module re-exports the benchmark layer's public names: the shipped (u, v) tuple set and its construction.

`load_mc_tuples(size)` returns one size of the shipped set, `generate_mc_tuples` constructs an equivalent
set, and `MCTuples` holds either one.
"""

from ._core.benchmark import MC_TUPLES_SIZES, MCTuples, MCTuplesStats, generate_mc_tuples, load_mc_tuples

__all__ = ["MC_TUPLES_SIZES", "MCTuples", "MCTuplesStats", "generate_mc_tuples", "load_mc_tuples"]
