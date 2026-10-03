"""`RESULTS_SCHEMA` defines the columns and types of the benchmark results table, 1 row per solve.

Each row is 1 solver on 1 Monte Carlo sample of 1 test function.

The table stores only raw measurements, not values derived from them, such as an evaluation count adjusted
for failed solves or a flop cost weighted per flop type, so a change to how such values are derived never
leaves stored results stale.
"""

import polars as pl
from counted_float import FlopType

from sunnbear._core.solvers.core import SolveStatus


def solver_flop_count_column_name(flop_type: FlopType) -> str:
    """Return the name of the column that counts the solver's `flop_type` flops, e.g. `solver_flop_count_add`."""
    return f"solver_flop_count_{flop_type.name.lower()}"


RESULTS_SCHEMA: dict[str, pl.DataType] = {
    # These columns identify the solve.
    "solver_id": pl.String(),
    "solver_version": pl.Int32(),
    "function_id": pl.String(),
    "mc_size": pl.Int32(),
    "mc_sample_idx": pl.Int32(),
    # These columns hold the Monte Carlo sample: its (u, v) tuple and that tuple's (xtol, c) values.
    "u": pl.Float64(),
    "v": pl.Float64(),
    "xtol": pl.Float64(),
    "c": pl.Float64(),
    # This column holds the solve's evaluation limit, the same on every row of a run. The limit is stored on each row so
    # that the evaluation count of a failed solve can be replaced by the limit without reading the run info, even
    # after the rows of several runs are combined or filtered.
    "max_fevals": pl.Int32(),
    # These columns hold the raw measurements.
    "x_found": pl.Float64(),
    "status": pl.Enum([status.value for status in SolveStatus]),
    "n_fevals": pl.Int32(),
    "is_correct": pl.Boolean(),
    "wall_time_ns": pl.Int64(),
    # Each flop type gets 1 column that holds the raw count of the solver's own arithmetic; the function's
    # evaluations are not counted. The per-flop-type cost weights are applied at analysis time, because
    # counted-float can change them without any version number that records the change.
    **{solver_flop_count_column_name(flop_type): pl.Int32() for flop_type in FlopType},
}
