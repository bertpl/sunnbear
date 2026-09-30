"""`results_table` builds a small results table by hand, for the aggregation tests."""

import polars as pl

from sunnbear._core.benchmark.runner import RESULTS_SCHEMA


def results_table(rows: list[dict[str, object]]) -> pl.DataFrame:
    """Return a table with the columns of `RESULTS_SCHEMA`: each row's own values, and fixed values elsewhere.

    The fixed values are those of a converged, correct solve with no counted flops.
    """
    defaults: dict[str, object] = {
        "solver_id": "bisection",
        "solver_version": 1,
        "function_id": "f2.1.1[p1=0.2]",
        "mc_size": 32,
        "mc_sample_idx": 0,
        "u": 0.5,
        "v": 0.5,
        "xtol": 1e-10,
        "c": 0.0,
        "max_fevals": 160,
        "x_found": 0.0,
        "status": "converged",
        "n_fevals": 10,
        "is_correct": True,
        "wall_time_ns": 1000,
    }
    return pl.from_dicts(
        [{column: row.get(column, defaults.get(column, 0)) for column in RESULTS_SCHEMA} for row in rows],
        schema=RESULTS_SCHEMA,
    )
