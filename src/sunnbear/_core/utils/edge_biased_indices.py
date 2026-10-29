"""This module selects indices into a sorted array, with more of them near both ends of the array."""

import math

import numpy as np


def select_edge_biased_indices(*, n_selected: int, n_values: int) -> np.ndarray:
    """Return `n_selected` sorted indices into an array of `n_values` values, closer together near both ends.

    The left half of the indices starts at 0 and 1, and the gaps between consecutive indices grow geometrically with
    ratio r, 1, r, r^2, and so on, up to the gap between the 2 middle indices.

    The right half mirrors the left one, so index `i` is selected exactly when `n_values - 1 - i` is.

    The ratio r is the one at which the last index reaches `n_values - 1` while the gap between the 2 middle indices is
    the next term of the sequence, r^(n_selected/2 - 1). The indices are computed as real numbers and then rounded to
    the nearest integer, so each gap differs from its term of the sequence by at most 1.

    Args:
        n_selected: The number of indices; even, so that the selection can be symmetric, and at least 4, so that each
            half holds at least 2 indices.
        n_values: The length of the indexed array; at least `n_selected`. When it equals `n_selected`, r is 1 and every
            index is selected.

    Returns:
        An int64 array of `n_selected` distinct indices in ascending order, starting at 0 and 1 and ending at
        `n_values - 2` and `n_values - 1`.

    Raises:
        ValueError: If `n_selected` is odd or below 4, or if `n_values` is below `n_selected`.
    """
    if n_selected % 2 != 0 or n_selected < 4:
        raise ValueError(f"n_selected must be even and at least 4 (got {n_selected}).")
    elif n_values < n_selected:
        raise ValueError(f"n_values must be at least n_selected = {n_selected} (got {n_values}).")
    else:
        n_per_half = n_selected // 2
        gap_ratio = _compute_gap_ratio(n_per_half=n_per_half, n_values=n_values)
        left_positions = np.concatenate(([0.0], np.cumsum(gap_ratio ** np.arange(n_per_half - 1))))
        # Rounding half up never shrinks a gap of at least 1 below 1, so the indices stay distinct; np.round rounds
        # half to even, which can map 2 positions 1 apart, such as 1.5 and 2.5, to the same integer.
        left_indices = np.floor(left_positions + 0.5).astype(np.int64)
        return np.concatenate((left_indices, n_values - 1 - left_indices[::-1]))


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _compute_gap_ratio(*, n_per_half: int, n_values: int) -> float:
    """Return the ratio r that places the 2 middle indices symmetrically about `(n_values - 1) / 2`.

    The left half's gaps are 1, r, ..., r^(n_per_half - 2), and the gap after them, between the 2 middle indices, is
    r^(n_per_half - 1).
    """
    # The sum of the left half's gaps and half the gap between the 2 middle indices grows with r, so bisection
    # finds r between 2 values: at r = 1 the sum is at most the center, (n_values - 1) / 2; at the upper value,
    # r^(n_per_half - 1) equals n_values - 1, so half the gap between the 2 middle indices alone reaches the
    # center, the sum is above it, and no power overflows float64.
    lo, hi = 1.0, (n_values - 1) ** (1 / (n_per_half - 1))
    mid = (lo + hi) / 2
    # Stop once no float64 lies strictly between lo and hi, so r is exact to float64 precision.
    while mid not in (lo, hi):
        gaps = [mid**j for j in range(n_per_half)]
        overshoot = math.fsum(gaps[:-1]) + gaps[-1] / 2 - (n_values - 1) / 2
        if overshoot < 0:
            lo = mid
        else:
            hi = mid
        mid = (lo + hi) / 2
    return lo
