"""This module re-exports the benchmark layer's public names: the Monte Carlo (MC) tuples, the runs and their analysis.

A benchmark run solves every test function with every solver at every (u, v) tuple of the chosen MC tuple set size,
each tuple mapped to a tolerance `xtol` and a value of the function's parameter `c`, and stores 1 row per solve.

- `load_mc_tuples(size)` returns one size of the shipped (u, v) tuple set, which every run uses; `generate_mc_tuples`
  constructs an equivalent set, and `MCTuples` holds either one;
- `run_benchmark` runs the solvers and writes the rows to a run directory, which `load_results` reads back as a
  results table with the columns of `RESULTS_SCHEMA`;
- `compute_xtol_range` returns the range of `xtol` values on which bisection spends exactly a given number of
  function evaluations, and `is_solution_correct` checks whether a root lies within `xtol` of a solver's answer;
- `DEFAULT_N_BISECTION_FEVALS` is the default of `run_benchmark`'s `n_bisection_fevals`, the number of function
  evaluations that bisection spends to reach each solve's `xtol`;
- every solve's evaluation budget is `MAX_FEVALS_FACTOR` times `n_bisection_fevals`;
- `add_derived_results` adds the columns of `DERIVED_RESULTS_SCHEMA` to a results table; these columns hold the metrics
  for comparing solvers, such as flop costs;
- `summarize_results` summarizes a results table per group, e.g. per solver.
"""

from ._core.benchmark import (
    DEFAULT_N_BISECTION_FEVALS,
    DERIVED_RESULTS_SCHEMA,
    MAX_FEVALS_FACTOR,
    RESULTS_SCHEMA,
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
    "DEFAULT_N_BISECTION_FEVALS",
    "DERIVED_RESULTS_SCHEMA",
    "MAX_FEVALS_FACTOR",
    "RESULTS_SCHEMA",
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
