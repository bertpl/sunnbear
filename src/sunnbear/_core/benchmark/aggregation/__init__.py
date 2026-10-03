"""This package holds the functions that analyze benchmark results: each takes a results table and returns a new table.

- `add_derived_results` adds the metrics for comparing solvers, such as flop costs and an evaluation count adjusted for
  failed solves;
- `summarize_results` returns 1 row per group of the caller's choice, with the fractions of converged and of correct
  solves, and `gpq` (geometric pseudo-quantile) values at chosen levels.

Every function takes a `DataFrame` or a `LazyFrame` and returns the same kind, so the functions can be mixed at any
point with ordinary polars operations, such as a filter.

The functions read their inputs, such as a solve's evaluation budget, from columns of the results table, so
their results stay correct after rows are filtered or runs are combined.
"""

from .derived_results import (
    DERIVED_RESULTS_SCHEMA,
    FEVAL_FLOP_COSTS,
    add_derived_results,
    total_flop_cost_column_name,
)
from .summary import DEFAULT_GPQ_LEVELS, gpq_column_name, summarize_results
