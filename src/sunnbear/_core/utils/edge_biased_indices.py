"""This module selects indices into a sorted array, with more of them near both ends of the array."""

import math

import numpy as np


def select_edge_biased_indices(*, n_selected: int, n_total: int) -> np.ndarray:
    """Return `n_selected` sorted indices into `n_total` values, closer together near both ends than in the middle.

    The left half of the indices starts at 0 and 1, and the gaps between consecutive indices grow geometrically,
    1, r, r^2, and so on, up to the gap between the 2 middle indices; the right half mirrors the left one, so index
    `i` is selected exactly when `n_total - 1 - i` is.

    The ratio r is chosen so that the gap between the 2 middle indices is the next term of the sequence,
    r^(n_selected/2 - 1). The indices are computed as real numbers and then rounded to the nearest integer, so each
    gap differs from its term of the sequence by at most 1.

    Args:
        n_selected: The number of indices; even, so that the selection can be symmetric, and at least 4, so that each
            half holds at least 2 indices.
        n_total: The length of the indexed array; at least `n_selected`. When it equals `n_selected`, r is 1 and every
            index is selected.

    Returns:
        An int64 array of `n_selected` distinct indices in ascending order, starting at 0 and 1 and ending at
        `n_total - 2` and `n_total - 1`.

    Raises:
        ValueError: If `n_selected` is odd or below 4, or if `n_total` is below `n_selected`.
    """
    if n_selected % 2 != 0 or n_selected < 4:
        raise ValueError(f"n_selected must be even and at least 4 (got {n_selected}).")
    elif n_total < n_selected:
        raise ValueError(f"n_total must be at least n_selected = {n_selected} (got {n_total}).")
    else:
        n_per_half = n_selected // 2
        gap_ratio = _compute_gap_ratio(n_per_half=n_per_half, n_total=n_total)
        positions = np.concatenate(([0.0], np.cumsum(gap_ratio ** np.arange(n_per_half - 1))))
        # Rounding half up never shrinks a gap of at least 1 below 1, so the indices stay distinct; np.round rounds
        # half to even, which can map 2 positions 1 apart, such as 1.5 and 2.5, to the same integer.
        left_indices = np.floor(positions + 0.5).astype(np.int64)
        return np.concatenate((left_indices, n_total - 1 - left_indices[::-1]))


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _compute_gap_ratio(*, n_per_half: int, n_total: int) -> float:
    """Return the ratio r at which the left half's gaps, plus half of the gap after them, sum to `(n_total - 1) / 2`.

    The left half's gaps are 1, r, ..., r^(n_per_half - 2), and the gap after them, between the 2 middle indices, is
    r^(n_per_half - 1). The sum of the left half's gaps and half the gap between the 2 middle indices grows with r, so
    bisection finds r between 2 values:

    - at r = 1, the sum is at most the center, `(n_total - 1) / 2`;
    - at r = `(n_total - 1)^(1 / (n_per_half - 1))`, half the gap between the 2 middle indices alone reaches the
      center, so the sum is above it. At this r, the largest power, r^(n_per_half - 1), equals `n_total - 1`, so no
      power overflows float64.
    """
    lo, hi = 1.0, (n_total - 1) ** (1 / (n_per_half - 1))
    mid = (lo + hi) / 2
    # Stop once no float64 lies strictly between lo and hi, so r is exact to float64 precision.
    while mid not in (lo, hi):
        gaps = [mid**j for j in range(n_per_half)]
        overshoot = math.fsum(gaps[:-1]) + gaps[-1] / 2 - (n_total - 1) / 2
        if overshoot < 0:
            lo = mid
        else:
            hi = mid
        mid = (lo + hi) / 2
    return lo
