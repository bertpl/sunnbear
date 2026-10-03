"""`owg_expression` and `gpq_expression` compute `owg` and `gpq` per group inside polars, matching `pseudo_quantiles`.

The statistics are `owg`, the ordered weighted geometric mean, and `gpq`, the geometric pseudo-quantile, whose
numpy functions are in `pseudo_quantiles`. Calling the numpy functions once per group would run Python code for
every group, which is slow on a results table with many groups; these expressions run inside polars.

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

    In each case, the expression returns what `owg` returns:

    - the exact maximum at power `+inf` and the exact minimum at power `-inf`;
    - 0 for a group that contains a zero;
    - the rank-weighted geometric mean otherwise.

    Unlike `owg`, the expression cannot refuse invalid values:

    - a negative value gives NaN;
    - a group of only nulls gives null;
    - a null among other values gives a wrong result, because it still counts toward the rank weights.
    """
    values = pl.col(column).cast(pl.Float64)

    # --- cases with an exact result -------------
    if p == float("inf"):
        return values.max()
    elif p == float("-inf"):
        return values.min()
    else:
        # --- sort & weight ----------------------
        log_values = values.sort(descending=p < 0).log()
        rank_fractions = (pl.int_range(pl.len()).cast(pl.Float64) + 0.5) / pl.len()
        weights = rank_fractions.pow(abs(p))

        # --- weighted geometric mean ------------
        # A zero gives 0 directly, as in `owg`: the weight on the zero can round down to 0.0 in float64, and
        # 0.0 * log(0) would give NaN.
        weighted_geometric_mean = ((weights * log_values).sum() / weights.sum()).exp()
        return pl.when(values.min() == 0.0).then(0.0).otherwise(weighted_geometric_mean)


# ==================================================================================================
#  Geometric pseudo-quantile
# ==================================================================================================
def gpq_expression(column: str, q: float) -> pl.Expr:
    """Return an aggregation expression that computes `gpq` of `column` at level `q`, per group.

    Like `owg_expression`, the expression cannot refuse invalid values: a negative value gives NaN, a group of only
    nulls gives null, and a null among other values gives a wrong result.

    Raises:
        ValueError: If `q` is NaN or outside the interval [0, 1].
    """
    return owg_expression(column, gpq_power_for_level(q))
