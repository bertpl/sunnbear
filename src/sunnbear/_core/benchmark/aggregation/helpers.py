"""The aggregation functions share these helpers."""

import polars as pl

from sunnbear._core.solvers.core import SolveStatus


def is_converged_expression() -> pl.Expr:
    """Return an expression that is true for a solve that converged, whether its answer is correct or not."""
    return pl.col("status") == SolveStatus.CONVERGED.value
