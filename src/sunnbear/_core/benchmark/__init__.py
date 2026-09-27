"""This package holds the benchmark layer: the (u, v) tuple set that drives every Monte Carlo benchmark run.

Importing it registers the `mc_tuples` artifact declaration with `ArtifactRegistry`.
"""

from .mc_tuples import MC_TUPLES_SIZES, MCTuples, MCTuplesStats, generate_mc_tuples, mc_tuples

__all__ = ["MC_TUPLES_SIZES", "MCTuples", "MCTuplesStats", "generate_mc_tuples", "mc_tuples"]
