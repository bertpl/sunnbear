"""This package holds the aggregation of benchmark results: plain functions that take a results table and return one.

- `add_derived_results` adds the values that the benchmark compares, such as the evaluation count with failed
  solves counted at the evaluation budget, and flop costs;
- `summarize_results` returns 1 row per group of the caller's choice, with success fractions and `gpq` levels.

Every function takes an eager or a lazy frame and returns the same kind, so the steps chain in any order with
ordinary polars operations, such as a filter between them. The facts that the functions need, such as a
solve's evaluation budget, are columns of the results table, so they hold after any filter or combination of
runs.
"""

from .derived_results import (
    DERIVED_RESULTS_SCHEMA,
    FEVAL_FLOP_COSTS,
    add_derived_results,
    total_flop_cost_column_name,
)
from .summary import DEFAULT_GPQ_LEVELS, gpq_column_name, summarize_results
