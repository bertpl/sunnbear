"""`owg`, the ordered weighted geometric mean, as a numpy function and as a polars expression.

The ordered weighted geometric mean weights sorted samples by a power law of their rank, so that the statistic
ranges continuously from the minimum through the geometric mean to the maximum as its power varies. `gpq`
(`geometric_pseudo_quantile`) calibrates that power to a quantile level.

`owg_expression` computes the statistic per group inside polars: calling `owg` once per group would run Python
code for every group, which is slow on a results table with many groups.
"""

import numpy as np
import polars as pl
from numpy.typing import ArrayLike


# ==================================================================================================
#  owg
# ==================================================================================================
def owg(values: ArrayLike, p: float) -> float:
    """Compute the ordered weighted geometric mean of non-negative samples.

    Sorts the values (ascending for ``p >= 0``, descending for ``p < 0``) and
    weights each by ``rank_fractions ** |p|``, where the rank fractions are the
    interval midpoints ``(i + 0.5) / n``. The result ranges from ``min(values)``
    (``p = -inf``) through the plain geometric mean (``p = 0``) to
    ``max(values)`` (``p = +inf``).

    A single zero among the values makes the result 0, as it does for any
    geometric mean, because every weight is mathematically positive for a
    finite ``p``.

    Args:
        values: Non-negative samples; at least one required.
        p: Tail-emphasis power; positive emphasizes large values, negative
            emphasizes small ones. ``+inf`` and ``-inf`` give the exact
            maximum and minimum.

    Returns:
        The weighted geometric mean ``exp(sum(w * ln(v)) / sum(w))``, except:

        - 0 if any value is 0 and ``p`` is finite;
        - ``max(values)`` for ``p = +inf``;
        - ``min(values)`` for ``p = -inf``.

    Raises:
        ValueError: If `values` is empty or contains negative entries.
    """
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        raise ValueError("owg requires at least one value.")
    if np.any(v < 0.0):
        raise ValueError("owg requires non-negative values.")

    # --- cases with an exact result -------------
    if p == np.inf:
        return float(np.max(v))
    elif p == -np.inf:
        return float(np.min(v))
    elif np.any(v == 0.0):
        # Return 0 directly: for a large |p| and many values, the weight on the
        # zero can round down to 0.0 in float64, and 0.0 * log(0) would give NaN.
        return 0.0

    # --- sort & weight --------------------------
    v_sorted = np.sort(v) if p >= 0 else np.sort(v)[::-1]
    n = v_sorted.size
    rank_fractions = np.linspace(0.5 / n, 1.0 - 0.5 / n, n)
    # Dividing by the largest rank fraction makes the largest weight exactly 1: for a large |p|, the raw weights
    # would all round down to 0.0 and give 0 / 0. A factor common to all weights leaves the result unchanged.
    weights = (rank_fractions / rank_fractions[-1]) ** abs(p)

    # --- weighted geometric mean ----------------
    return float(np.exp(np.sum(weights * np.log(v_sorted)) / np.sum(weights)))


# ==================================================================================================
#  Polars expression
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
        # As in `owg`, dividing by the largest rank fraction keeps the largest weight at exactly 1.
        weights = (rank_fractions / rank_fractions.max()).pow(abs(p))

        # --- weighted geometric mean ------------
        # A zero gives 0 directly, as in `owg`: the weight on the zero can round down to 0.0 in float64, and
        # 0.0 * log(0) would give NaN.
        weighted_geometric_mean = ((weights * log_values).sum() / weights.sum()).exp()
        return pl.when(values.min() == 0.0).then(0.0).otherwise(weighted_geometric_mean)
