"""This package holds the benchmark layer.

It holds the (u, v) tuple set that drives every Monte Carlo benchmark run, and the tolerances and evaluation
budget derived from bisection's evaluation count.

Importing it registers the `mc_tuples` artifact declaration with `ArtifactRegistry`.
"""

from .mc_tuples import MC_TUPLES_SIZES, MCTuples, MCTuplesStats, generate_mc_tuples, load_mc_tuples

__all__ = ["MC_TUPLES_SIZES", "MCTuples", "MCTuplesStats", "generate_mc_tuples", "load_mc_tuples"]
