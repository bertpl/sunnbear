"""This module re-exports the benchmark layer's public names: the shipped Monte Carlo (MC) tuple set and its generation.

The MC tuples are the (u, v) tuples that every Monte Carlo benchmark run samples from.

`load_mc_tuples(size)` returns one size of the shipped set, `generate_mc_tuples` constructs an equivalent
set, and `MCTuples` holds either one.
"""

from ._core.benchmark import MCTuples, MCTuplesSize, MCTuplesStats, generate_mc_tuples, load_mc_tuples

__all__ = ["MCTuples", "MCTuplesSize", "MCTuplesStats", "generate_mc_tuples", "load_mc_tuples"]
