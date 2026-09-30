"""`MCTuplesBinDefinitions` defines the bins of each axis that a tuple set of a given size is balanced over."""

import math
from dataclasses import dataclass

import numpy as np


# ==================================================================================================
#  MCTuplesBinDefinitions
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesBinDefinitions:
    """`MCTuplesBinDefinitions` defines the equal bins of each axis for a tuple set of `size` tuples, and their bounds.

    Each axis, u and v, is cut into `n_bins = ⌊√size⌋` equal bins, as in a histogram, and a balanced set holds
    `round(size / n_bins) ± 1` of its tuples in each bin. Each bin is then about as wide as the spacing
    `1/(√size - 1)` of `size` tuples on a square grid, so the bins balance the tuples along each axis at the
    scale at which min separation spreads them in the square: a fixed number of bins would balance them more
    loosely as the size grows, and narrower bins cost more spread the larger the size.

    The bounds can always be met: `n_bins · min_count_per_bin ≤ size ≤ n_bins · max_count_per_bin`, because
    the rounded count lies within 1/2 of `size / n_bins`.

    Attributes:
        size: The number of tuples in the set, at least 2.
    """

    size: int

    def __post_init__(self) -> None:
        """Check the size.

        Raises:
            ValueError: If `size` is below 2, the smallest tuple set.
        """
        if self.size < 2:
            raise ValueError(f"A tuple set holds at least 2 tuples (got {self.size}).")

    # --------------------------------------------------------------------------
    #  Bins and bounds
    # --------------------------------------------------------------------------
    @property
    def n_bins(self) -> int:
        """Return the number of equal bins of each axis, `⌊√size⌋`."""
        return math.isqrt(self.size)

    @property
    def min_count_per_bin(self) -> int:
        """Return the fewest tuples that a bin of a balanced set holds, `round(size / n_bins) - 1`."""
        return self._target_count_per_bin - 1

    @property
    def max_count_per_bin(self) -> int:
        """Return the most tuples that a bin of a balanced set holds, `round(size / n_bins) + 1`."""
        return self._target_count_per_bin + 1

    def bin_indices(self, values: np.ndarray) -> np.ndarray:
        """Return, for each value in (0, 1), the index of the bin that holds it."""
        return np.minimum((values * self.n_bins).astype(np.int64), self.n_bins - 1)

    def bin_counts(self, values: np.ndarray) -> tuple[int, ...]:
        """Return the number of values in each bin, from the bin at 0 to the bin at 1."""
        return tuple(int(n) for n in np.bincount(self.bin_indices(values), minlength=self.n_bins))

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @property
    def _target_count_per_bin(self) -> int:
        """Return `round(size / n_bins)`, the middle of the bounds."""
        return round(self.size / self.n_bins)
