"""This package holds the benchmark layer.

It holds:

- `mc_tuples`: the (u, v) tuple set that drives every Monte Carlo benchmark run;
- `protocol`: the rules that every solve follows: its tolerances and evaluation budget, its seeds, and
  the check of whether the solver's answer is correct;
- `runner`: `run_benchmark`, which runs the benchmark tasks of a run and writes their results to a run
  directory, and `load_results`, which reads 1 or more runs back as 1 table;
- `aggregation`: `add_derived_results`, which adds derived columns, such as flop costs, to a results table, and
  `summarize_results`, which summarizes a results table per group.

Importing it registers the `mc_tuples` artifact declaration with `ArtifactRegistry`.
"""

from .mc_tuples import MCTuples, MCTuplesSize, MCTuplesStats, generate_mc_tuples, load_mc_tuples

__all__ = [
    "MCTuples",
    "MCTuplesSize",
    "MCTuplesStats",
    "generate_mc_tuples",
    "load_mc_tuples",
]
