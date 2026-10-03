"""This package holds the aggregation of benchmark results: functions from a results table to a new table.

`add_derived_results` adds the values that solvers are compared on, such as the evaluation count with failed solves
counted at the evaluation budget, and flop costs.

Every function takes an eager or a lazy frame and returns the same kind: it builds its result as a lazy query on
`frame.lazy()` and returns it through `collect_if_eager`. The functions can therefore be mixed at any point with
ordinary polars operations, such as a filter.

The functions read their inputs, such as a solve's evaluation budget, from columns of the results table, so
their results stay correct after rows are filtered or runs are combined.
"""

from .derived_results import (
    DERIVED_RESULTS_SCHEMA,
    FEVAL_FLOP_COSTS,
    add_derived_results,
    total_flop_cost_column_name,
)
