"""This module re-exports the benchmark layer's public names: the Monte Carlo (MC) tuples, the runs and their analysis.

A benchmark run solves every test function with every solver at every sample of the MC tuple set, and stores 1 row
per solve.

- `load_mc_tuples(size)` returns one size of the shipped (u, v) tuple set, which every run samples from;
  `generate_mc_tuples` constructs an equivalent set, and `MCTuples` holds either one;
- `run_benchmark` runs the solvers and writes the rows to a run directory, which `load_results` reads back as a
  results table; `compute_xtol_range` and `is_solution_correct` are 2 of the rules that every solve follows: the
  tolerance range derived from bisection's evaluation count, and the check of whether an answer is a root;
- `add_derived_results` adds the metrics for comparing solvers, such as flop costs, to a results table, and
  `summarize_results` summarizes a results table per group, e.g. per solver.

What each piece does is described in the docstring of the implementation package, `sunnbear._core.benchmark`.
"""

from ._core.benchmark import (
    MCTuples,
    MCTuplesSize,
    MCTuplesStats,
    add_derived_results,
    compute_xtol_range,
    generate_mc_tuples,
    is_solution_correct,
    load_mc_tuples,
    load_results,
    run_benchmark,
    summarize_results,
)

__all__ = [
    "MCTuples",
    "MCTuplesSize",
    "MCTuplesStats",
    "add_derived_results",
    "compute_xtol_range",
    "generate_mc_tuples",
    "is_solution_correct",
    "load_mc_tuples",
    "load_results",
    "run_benchmark",
    "summarize_results",
]
