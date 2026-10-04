"""`add_derived_results` adds the columns of `DERIVED_RESULTS_SCHEMA`, computed from a results table's raw measurements.

The results table stores only raw measurements (see `RESULTS_SCHEMA`); the metrics for comparing solvers
are derived from them when a table is analyzed. The docstring of `add_derived_results` describes each derived
column, because its callers read that docstring and not this one.
"""

from typing import overload

import polars as pl
from counted_float import FlopType
from counted_float.config import get_active_flop_weights

from sunnbear._core.benchmark.runner import solver_flop_count_column_name

# Each value is an assumed cost of 1 function evaluation, in flops; `add_derived_results` adds 1
# `total_flop_cost_feval<k>` column per value.
FEVAL_FLOP_COSTS = (10, 100, 1000)


def total_flop_cost_column_name(feval_flop_cost: int) -> str:
    """Return the name of the total flop cost column for `feval_flop_cost`, the assumed flops per function evaluation.

    E.g. `total_flop_cost_feval100` for 100 flops per evaluation.
    """
    return f"total_flop_cost_feval{feval_flop_cost}"


DERIVED_RESULTS_SCHEMA: dict[str, pl.DataType] = {
    "n_fevals_eff": pl.Int32(),
    "solver_flop_cost": pl.Float64(),
    **{total_flop_cost_column_name(feval_flop_cost): pl.Float64() for feval_flop_cost in FEVAL_FLOP_COSTS},
}


# The overloads promise the type checker that a `DataFrame` in gives a `DataFrame` out and a `LazyFrame` in a
# `LazyFrame` out; without them the return type is the union, and every caller would have to narrow it.
@overload
def add_derived_results(frame: pl.DataFrame) -> pl.DataFrame: ...
@overload
def add_derived_results(frame: pl.LazyFrame) -> pl.LazyFrame: ...
def add_derived_results(frame: pl.DataFrame | pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame:
    """Return `frame` with the columns of `DERIVED_RESULTS_SCHEMA` added, computed from its raw measurements.

    The added columns are:

    - `n_fevals_eff`: the solve's evaluation count, `n_fevals`, when its answer is correct, and the row's
      `max_fevals`, its whole evaluation budget, for any other solve, so a failed solve counts as if it spent its
      whole budget;
    - `solver_flop_cost`: the sum of the flop counts of the solver's own arithmetic, each weighted by the cost of
      its flop type; a failed solve keeps its actual flop counts, and only its evaluation count is replaced by the
      budget, in `n_fevals_eff`;
    - `total_flop_cost_feval<k>`: `solver_flop_cost + k · n_fevals_eff`, the cost of a solve in flops when 1
      function evaluation costs `k` flops, for `k` of 10, 100 and 1000.

    The flop counts are weighted with counted-float's active flop weights, read when this function is called:
    `counted_float.config.set_active_flop_weights` changes the active flop weights for later calls, not for a lazy
    frame that this function already returned.

    Args:
        frame: A results table with the columns of `RESULTS_SCHEMA`.

    Raises:
        ValueError: If a weight of counted-float's active flop weights is unknown (NaN).
    """
    flop_weights = get_active_flop_weights()
    if flop_weights.has_missing_data():
        raise ValueError(
            "counted-float's active flop weights hold an unknown (NaN) weight; "
            "give every flop type a weight with counted_float.config.set_active_flop_weights."
        )

    # --- evaluation counts, solver cost ---------
    n_fevals_eff = pl.when(pl.col("is_correct")).then(pl.col("n_fevals")).otherwise(pl.col("max_fevals"))
    solver_flop_cost = pl.sum_horizontal(
        pl.col(solver_flop_count_column_name(flop_type)) * float(flop_weights.weights[flop_type])
        for flop_type in FlopType
    )
    derived = frame.lazy().with_columns(
        n_fevals_eff.alias("n_fevals_eff"),
        solver_flop_cost.alias("solver_flop_cost"),
    )

    # --- total costs ----------------------------
    derived = derived.with_columns(
        (pl.col("solver_flop_cost") + feval_flop_cost * pl.col("n_fevals_eff")).alias(
            total_flop_cost_column_name(feval_flop_cost)
        )
        for feval_flop_cost in FEVAL_FLOP_COSTS
    )
    # The caller gets back the kind it passed in: a `DataFrame` is collected, a `LazyFrame` stays a plan.
    if isinstance(frame, pl.DataFrame):
        return derived.collect()
    else:
        return derived
