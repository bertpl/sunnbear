"""This package holds the functions that analyze benchmark results: each takes a results table and returns a new table.

`add_derived_results` adds the metrics for comparing solvers, such as flop costs and the evaluation count, in which a
failed solve counts as if it spent its whole evaluation budget.

Every function takes an eager or a lazy frame and returns the same kind, so the functions can be mixed at any point
with ordinary polars operations, such as a filter.

The functions read their inputs, such as a solve's evaluation budget, from columns of the results table, so
their results stay correct after rows are filtered or runs are combined.
"""

from .derived_results import (
    DERIVED_RESULTS_SCHEMA,
    FEVAL_FLOP_COSTS,
    add_derived_results,
    total_flop_cost_column_name,
)
