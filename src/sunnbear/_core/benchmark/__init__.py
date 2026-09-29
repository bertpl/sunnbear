"""This package holds the benchmark layer.

It holds:

- the (u, v) tuple set that drives every Monte Carlo benchmark run;
- the tolerances and evaluation budget derived from bisection's evaluation count;
- the seeds derived from a run's root seed, and the check of whether a solver's answer is correct;
- the benchmark task, which runs every solver on 1 test function, and `run_benchmark`, which runs the
  tasks of a run and writes their results to a run directory that `load_results` reads back.

Importing it registers the `mc_tuples` artifact declaration with `ArtifactRegistry`.
"""

from .mc_tuples import MC_TUPLES_SIZES, MCTuples, MCTuplesStats, generate_mc_tuples, load_mc_tuples

__all__ = ["MC_TUPLES_SIZES", "MCTuples", "MCTuplesStats", "generate_mc_tuples", "load_mc_tuples"]
