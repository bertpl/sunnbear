"""This package holds the aggregation of benchmark results: functions from a results table to a new table.

- `add_derived_results` adds the benchmark's comparison values, such as the evaluation count with failed solves
  counted at the evaluation budget, and flop costs;
- `summarize_results` returns 1 row per group of the caller's choice, with success fractions and `gpq`
  (geometric pseudo-quantile) levels.

Every function takes an eager or a lazy frame and returns the same kind, so the functions can be called in any
order, mixed with ordinary polars operations such as a filter.

The inputs of the functions, such as a solve's evaluation budget, are columns of the results table, so they
stay correct after any filter or combination of runs.
"""

from .derived_results import (
    DERIVED_RESULTS_SCHEMA,
    FEVAL_FLOP_COSTS,
    add_derived_results,
    total_flop_cost_column_name,
)
from .summary import DEFAULT_GPQ_LEVELS, gpq_column_name, summarize_results
