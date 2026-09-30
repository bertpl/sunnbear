"""This module builds polars expressions for 2 statistics per group, with the results of their numpy functions.

The statistics are `owg`, the ordered weighted geometric mean, and `gpq`, the geometric pseudo-quantile, whose
numpy functions are in `pseudo_quantiles`. Calling the numpy functions once per group would run Python code for
every group, which is slow on a results table with many groups; these expressions run inside polars.

They follow `owg` and `gpq` case by case:

- the exact extremes at infinite powers;
- 0 for a group that contains a zero;
- the rank-weighted geometric mean otherwise.

These expressions are kept apart from `pseudo_quantiles`, so that importing the numpy functions does not
import polars.
"""

import polars as pl

from .pseudo_quantiles import gpq_power_for_level


# ==================================================================================================
#  Ordered weighted geometric mean
# ==================================================================================================
def owg_expression(column: str, p: float) -> pl.Expr:
    """Return an aggregation expression that computes `owg` of `column` at power `p`, per group.

    Unlike `owg`, the expression cannot refuse invalid values: a negative value gives NaN, and a group of
    only nulls gives null.
    """
    values = pl.col(column).cast(pl.Float64)
    if p == float("inf"):
        return values.max()
    elif p == float("-inf"):
        return values.min()
    else:
        # --- sort & weight ----------------------
        logs = values.sort(descending=p < 0).log()
        rank_ramp = (pl.int_range(pl.len()).cast(pl.Float64) + 0.5) / pl.len()
        weights = rank_ramp.pow(abs(p))

        # --- weighted geometric mean ------------
        # A zero gives 0 directly, as in `owg`: the weight on the zero can round down to 0.0 in float64, and
        # 0.0 * log(0) would give NaN.
        weighted_geometric_mean = ((weights * logs).sum() / weights.sum()).exp()
        return pl.when(values.min() == 0.0).then(0.0).otherwise(weighted_geometric_mean)


# ==================================================================================================
#  Geometric pseudo-quantile
# ==================================================================================================
def gpq_expression(column: str, q: float) -> pl.Expr:
    """Return an aggregation expression that computes `gpq` of `column` at level `q`, per group.

    Raises:
        ValueError: If `q` is NaN or outside the interval [0, 1].
    """
    return owg_expression(column, gpq_power_for_level(q))
