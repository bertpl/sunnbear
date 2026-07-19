"""Geometric pseudo-quantiles: smooth, log-space stand-ins for hard quantiles.

The ordered weighted geometric mean (OWG) weights sorted samples by a power law
of their rank, yielding a statistic that slides continuously between ``min``,
geometric mean, and ``max`` as its power parameter varies. `gpq` calibrates that
power so the weight distribution's center of mass sits at a requested quantile
level, giving a smooth alternative to ``np.quantile`` for strictly positive,
log-scaled samples (such as function-evaluation counts), which ordinary
quantiles summarize poorly because they snap to the few observed small-integer
values.
"""

import numpy as np
from numpy.typing import ArrayLike


# ==================================================================================================
#  Ordered weighted geometric mean
# ==================================================================================================
def owg(values: ArrayLike, p: float) -> float:
    """Compute the ordered weighted geometric mean of strictly positive samples.

    Sorts the values (ascending for ``p >= 0``, descending for ``p < 0``) and
    weights each by ``rank_ramp ** |p|``, where the rank ramp runs over the
    interval midpoints ``(i + 0.5) / n``. The result slides from ``min(values)``
    (``p -> -inf``) through the plain geometric mean (``p = 0``) to
    ``max(values)`` (``p -> +inf``).

    Args:
        values: Strictly positive samples; at least one required.
        p: Tail-emphasis power; positive emphasizes large values, negative
            emphasizes small ones.

    Returns:
        The weighted geometric mean ``exp(sum(w * ln(v)) / sum(w))``.

    Raises:
        ValueError: If `values` is empty or contains non-positive entries.
    """
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        raise ValueError("owg requires at least one value.")
    if np.any(v <= 0.0):
        raise ValueError("owg requires strictly positive values.")

    # --- sort & weight --------------------------
    v_sorted = np.sort(v) if p >= 0 else np.sort(v)[::-1]
    n = v_sorted.size
    rank_ramp = np.linspace(0.5 / n, 1.0 - 0.5 / n, n)
    weights = rank_ramp ** abs(p)

    # --- weighted geometric mean ----------------
    return float(np.exp(np.sum(weights * np.log(v_sorted)) / np.sum(weights)))


# ==================================================================================================
#  Geometric pseudo-quantile
# ==================================================================================================
def gpq(values: ArrayLike, q: float) -> float:
    """Compute the geometric pseudo-quantile of strictly positive samples.

    An `owg` whose power is calibrated via ``p(q) = (2q - 1) / min(q, 1 - q)``
    so that the weight distribution's center of mass sits at quantile level `q`
    (in the large-n limit). ``gpq(x, 0.5)`` is the plain geometric mean; the
    result approaches ``min(x)`` / ``max(x)`` as `q` approaches 0 / 1. Note the
    calibration targets the *weight* center of mass, not the hard quantile
    value itself.

    Args:
        values: Strictly positive samples; at least one required.
        q: Quantile level, strictly between 0 and 1.

    Returns:
        The calibrated ordered weighted geometric mean.

    Raises:
        ValueError: If `q` is outside the open interval (0, 1), or `values`
            fails `owg` validation.
    """
    if not 0.0 < q < 1.0:
        raise ValueError(f"gpq requires 0 < q < 1 (got {q}).")
    p = (2.0 * q - 1.0) / min(q, 1.0 - q)
    return owg(values, p)
