"""`MCTuplesBinDefinitions` defines, for a tuple set of a given size, the bins of each axis and their tuple counts."""

import math
from dataclasses import dataclass

import numpy as np


# ==================================================================================================
#  MCTuplesBinDefinitions
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesBinDefinitions:
    """`MCTuplesBinDefinitions` defines the equal bins of each axis for a set of `size` tuples, and their count bounds.

    Each axis, u and v, is cut into `n_bins_per_axis = ⌊√size⌋` equal bins, as in a histogram, and a balanced
    set holds `round(size / n_bins_per_axis) ± 1` of its tuples in each bin.

    Each bin is then about as wide as the spacing `1/(√size - 1)` of `size` tuples on a square grid, so along
    each axis the tuple counts are kept even over intervals as wide as the distance between neighboring tuples
    in the square.

    The bounds can always be met, because `round(size / n_bins_per_axis)` lies within 1/2 of `size / n_bins_per_axis`:
    `n_bins_per_axis · min_count_per_bin ≤ size ≤ n_bins_per_axis · max_count_per_bin`.

    Attributes:
        size: The number of tuples in the set, at least 2.
    """

    size: int

    def __post_init__(self) -> None:
        """Check the size.

        Raises:
            ValueError: If `size` is below 2, the size of the smallest tuple set.
        """
        if self.size < 2:
            raise ValueError(f"A tuple set holds at least 2 tuples (got {self.size}).")

    # --------------------------------------------------------------------------
    #  Bins and bounds
    # --------------------------------------------------------------------------
    @property
    def n_bins_per_axis(self) -> int:
        """Return the number of equal bins of each axis, `⌊√size⌋`."""
        return math.isqrt(self.size)

    @property
    def min_count_per_bin(self) -> int:
        """Return the fewest tuples allowed in a bin of a balanced set, `round(size / n_bins_per_axis) - 1`."""
        return self._target_count_per_bin - 1

    @property
    def max_count_per_bin(self) -> int:
        """Return the most tuples allowed in a bin of a balanced set, `round(size / n_bins_per_axis) + 1`."""
        return self._target_count_per_bin + 1

    def bin_indices(self, values: np.ndarray) -> np.ndarray:
        """Return, for each value in (0, 1), the index of the bin that holds it."""
        return np.minimum((values * self.n_bins_per_axis).astype(np.int64), self.n_bins_per_axis - 1)

    def bin_counts(self, values: np.ndarray) -> tuple[int, ...]:
        """Return the number of values in each bin, from the bin at 0 to the bin at 1."""
        return tuple(int(n) for n in np.bincount(self.bin_indices(values), minlength=self.n_bins_per_axis))

    def are_counts_within_bounds(self, counts: tuple[int, ...]) -> bool:
        """Return whether every count lies from `min_count_per_bin` to `max_count_per_bin`."""
        return self.min_count_per_bin <= min(counts) and max(counts) <= self.max_count_per_bin

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @property
    def _target_count_per_bin(self) -> int:
        """Return `round(size / n_bins_per_axis)`, the middle of the bounds."""
        return round(self.size / self.n_bins_per_axis)
