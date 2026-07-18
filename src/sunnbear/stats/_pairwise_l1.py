"""Exact mean pairwise L1 distance in O(d * n log n), without a distance matrix.

The mean absolute difference between all pairs of values of one coordinate is
the *Gini mean difference* (Gini, 1912; also "mean absolute difference" in the
statistics literature — for positive data it equals twice the mean times the
Gini coefficient). It is computable from a single sort: with values sorted
ascending, element ``x_(j)`` (1-indexed) is the larger element of ``j - 1``
pairs and the smaller of ``n - j``, so the pairwise sum collapses to the
standard order-statistics identity ``sum_j (2j - n - 1) * x_(j)``. The L1
metric adds over dimensions, so the mean pairwise L1 distance of a vector set
is simply the sum of its per-dimension Gini mean differences — d sorts instead
of n(n-1)/2 distance evaluations.
"""

import numpy as np
from numpy.typing import ArrayLike


# ==================================================================================================
#  Gini mean difference (single dimension)
# ==================================================================================================
def gini_mean_difference(values: ArrayLike) -> float:
    """Compute the mean absolute difference over all pairs of a 1D sample.

    Args:
        values: One-dimensional sample; at least two values required.

    Returns:
        ``mean_{i<j} |x_i - x_j|``, computed exactly via the sorted-sum formula.

    Raises:
        ValueError: If `values` is not 1D or holds fewer than two values.
    """
    v = np.asarray(values, dtype=np.float64)
    if v.ndim != 1:
        raise ValueError(f"gini_mean_difference requires a 1D array (got {v.ndim}D).")
    n = v.size
    if n < 2:
        raise ValueError("gini_mean_difference requires at least two values.")

    v_sorted = np.sort(v)
    coefficients = 2.0 * np.arange(1, n + 1) - n - 1
    pair_sum = float(np.sum(coefficients * v_sorted))
    return pair_sum / (n * (n - 1) / 2)


# ==================================================================================================
#  Mean pairwise L1 distance (vector set)
# ==================================================================================================
def mean_pairwise_l1(vectors: ArrayLike) -> float:
    """Compute the mean pairwise L1 distance over a set of vectors.

    Exploits the additive decomposition of L1 over dimensions: the result is
    the sum of the per-dimension `gini_mean_difference` values, so the cost is
    one sort per dimension rather than a pairwise distance matrix.

    Args:
        vectors: Array of shape ``(n, d)`` — n vectors of dimension d, n >= 2.

    Returns:
        ``mean_{i<j} ||x_i - x_j||_1``, exact over all pairs.

    Raises:
        ValueError: If `vectors` is not 2D or holds fewer than two vectors.
    """
    x = np.asarray(vectors, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError(f"mean_pairwise_l1 requires a 2D array (got {x.ndim}D).")
    if x.shape[0] < 2:
        raise ValueError("mean_pairwise_l1 requires at least two vectors.")
    return float(sum(gini_mean_difference(x[:, k]) for k in range(x.shape[1])))
