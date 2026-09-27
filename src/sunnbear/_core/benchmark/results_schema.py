"""`RESULTS_SCHEMA` fixes the columns and types of the benchmark results table, 1 row per solve.

Each row is 1 solver on 1 Monte Carlo sample of 1 test function. The identity columns come first, then the
raw measurements. Nothing derived is stored, such as a censored evaluation count or a weighted flop cost,
so a change to how those are derived never leaves stored results stale.
"""

import polars as pl
from counted_float import FlopType

from sunnbear._core.solvers.core import SolveStatus


def flops_column_name(flop_type: FlopType) -> str:
    """Return the name of the column that counts `flop_type`, e.g. `flops_add` for `FlopType.ADD`."""
    return f"flops_{flop_type.name.lower()}"


RESULTS_SCHEMA: dict[str, pl.DataType] = {
    # The identity of the solve.
    "solver_id": pl.String(),
    "solver_version": pl.Int32(),
    "function_id": pl.String(),
    "size": pl.Int32(),
    "mc_sample_idx": pl.Int32(),
    # The Monte Carlo sample: its (u, v) tuple, and the (xtol, c) values that it maps to.
    "u": pl.Float64(),
    "v": pl.Float64(),
    "xtol": pl.Float64(),
    "c": pl.Float64(),
    # The raw measurements.
    "x_found": pl.Float64(),
    "status": pl.Enum([status.value for status in SolveStatus]),
    "n_fevals": pl.Int32(),
    "correct": pl.Boolean(),
    "wall_time_ns": pl.Int64(),
    # 1 column per flop type, holding the raw count; the weights are applied at analysis time, because
    # counted-float's weights change without a version of their own.
    **{flops_column_name(flop_type): pl.Int32() for flop_type in FlopType},
}
