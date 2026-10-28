"""This module selects indices into a sorted array, with more of them near both ends of the array."""

import math

import numpy as np


def select_edge_biased_indices(*, n_selected: int, n_total: int) -> np.ndarray:
    """Return `n_selected` sorted indices into `n_total` values, closer together near both ends than in the middle.

    The left half of the indices starts at 0 and 1, and the gaps between consecutive indices grow geometrically,
    1, r, r^2, and so on, up to the gap across the center; the right half mirrors the left one, so index `i` is
    selected exactly when `n_total - 1 - i` is. The ratio r is the one at which the 2 halves meet: the gap across the
    center continues the geometric sequence. The positions are then rounded to the nearest integer, so the gaps
    follow the sequence to within 1.

    Args:
        n_selected: The number of indices; even, so that the selection can be symmetric, and at least 4, so that each
            half holds at least 2 indices.
        n_total: The number of values that the indices point into; at least `n_selected`. When it equals
            `n_selected`, r is 1 and every index is selected.

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
        n_left = n_selected // 2
        gap_ratio = _compute_gap_ratio(n_left=n_left, n_total=n_total)
        # The positions are the cumulative sums of the gaps 1, r, ..., r^(n_left - 2); rounding half up keeps every
        # gap of at least 1 at least 1, so the indices stay distinct.
        positions = np.concatenate(([0.0], np.cumsum(gap_ratio ** np.arange(n_left - 1))))
        left = np.floor(positions + 0.5).astype(np.int64)
        return np.concatenate((left, n_total - 1 - left[::-1]))


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _compute_gap_ratio(*, n_left: int, n_total: int) -> float:
    """Return the gap ratio r at which the left half, with half the gap across the center, ends at the center.

    The left half spans the gaps 1, r, ..., r^(n_left - 2), and the gap across the center is r^(n_left - 1). Their
    total grows with r, so bisection finds r between 2 values:

    - at r = 1, the total is at most the center, `(n_total - 1) / 2`;
    - at r = `(n_total - 1)^(1 / (n_left - 1))`, half the gap across the center alone reaches the center, so the total
      is above it; every power of r up to `n_total - 1` stays within float64's range.
    """
    lo, hi = 1.0, (n_total - 1) ** (1 / (n_left - 1))
    mid = (lo + hi) / 2
    while mid not in (lo, hi):
        gaps = [mid**j for j in range(n_left)]
        overshoot = math.fsum(gaps[:-1]) + gaps[-1] / 2 - (n_total - 1) / 2
        if overshoot < 0:
            lo = mid
        else:
            hi = mid
        mid = (lo + hi) / 2
    return lo
