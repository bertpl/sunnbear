"""`gpq`, the geometric pseudo-quantile, as a numpy function and as a polars expression.

A geometric pseudo-quantile is an `owg` (`ordered_weighted_geomean`) whose power is calibrated so that the weight
distribution's center of mass sits at a requested quantile level. It is a smooth alternative to ``np.quantile``
for positive, log-scaled samples, such as function-evaluation counts, which ordinary quantiles summarize poorly
because they snap to the few observed small-integer values.

`gpq_expression` computes the statistic per group inside polars: calling `gpq` once per group would run Python
code for every group, which is slow on a results table with many groups.
"""

import numpy as np
import polars as pl
from numpy.typing import ArrayLike

from .ordered_weighted_geomean import owg, owg_expression


# ==================================================================================================
#  gpq
# ==================================================================================================
def gpq(values: ArrayLike, q: float) -> float:
    """Compute the geometric pseudo-quantile of non-negative samples.

    An `owg` whose power is calibrated via ``p(q) = (2q - 1) / min(q, 1 - q)``
    so that the weight distribution's center of mass sits at quantile level `q`
    (in the large-n limit).

    ``gpq(x, 0.5)`` is the plain geometric mean, and ``gpq(x, 0)`` and
    ``gpq(x, 1)`` are exactly ``min(x)`` and ``max(x)``, because ``p(q)`` tends
    to ``-inf`` and ``+inf`` at those levels. The calibration aims at the
    *weight* center of mass, not at the hard quantile value itself.

    Args:
        values: Non-negative samples; at least one required. A zero makes the
            result 0 at every level below 1 (see `owg`).
        q: Quantile level, between 0 and 1 inclusive.

    Returns:
        The calibrated ordered weighted geometric mean.

    Raises:
        ValueError: If `q` is NaN or outside the interval [0, 1], or `values`
            fails `owg` validation.
    """
    return owg(values, gpq_power_for_level(q))


def gpq_power_for_level(q: float) -> float:
    """Return the `owg` power ``p(q) = (2q - 1) / min(q, 1 - q)`` of `gpq` at level `q`.

    The power is ``-inf`` at ``q = 0`` and ``+inf`` at ``q = 1``, the limits of
    the formula there.

    Raises:
        ValueError: If `q` is NaN or outside the interval [0, 1].
    """
    if not 0.0 <= q <= 1.0:
        raise ValueError(f"gpq requires 0 <= q <= 1 (got {q}).")

    if q == 0.0:
        return -np.inf
    elif q == 1.0:
        return np.inf
    else:
        return (2.0 * q - 1.0) / min(q, 1.0 - q)


# ==================================================================================================
#  Polars expression
# ==================================================================================================
def gpq_expression(column: str, q: float) -> pl.Expr:
    """Return an aggregation expression that computes `gpq` of `column` at level `q`, per group.

    Like `owg_expression`, the expression cannot refuse invalid values: a negative value gives NaN, a group of only
    nulls gives null, and a null among other values gives a wrong result.

    Raises:
        ValueError: If `q` is NaN or outside the interval [0, 1].
    """
    return owg_expression(column, gpq_power_for_level(q))
