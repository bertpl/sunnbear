"""Geometric pseudo-quantiles: smooth, log-space stand-ins for hard quantiles.

The ordered weighted geometric mean (OWG) weights sorted samples by a power law
of their rank, yielding a statistic that ranges continuously between ``min``,
geometric mean, and ``max`` as its power parameter varies. `gpq` calibrates that
power so the weight distribution's center of mass sits at a requested quantile
level, giving a smooth alternative to ``np.quantile`` for positive,
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
    weights = rank_fractions ** abs(p)

    # --- weighted geometric mean ----------------
    return float(np.exp(np.sum(weights * np.log(v_sorted)) / np.sum(weights)))


# ==================================================================================================
#  Geometric pseudo-quantile
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
