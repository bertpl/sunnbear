"""`MCTuplesSize` lists the sizes in which the shipped Monte Carlo tuple set comes; the fine lanes follow from them.

The construction corrects every size's u values and v values toward the same mean, `TARGET_MEAN`, and gives each value
at least `MIN_N_BITS` bits of information.
"""

from enum import IntEnum
from typing import NoReturn

import numpy as np

# `TARGET_MEAN` is the mean toward which the construction corrects every size's u values and v values.
TARGET_MEAN = 0.5

# `MIN_N_BITS` is the fewest bits of information (`n_bits`) that the construction leaves in any u value or v value, so
# that no short binary, decimal or rational description reproduces a value exactly; a random float64 value holds about
# 51 to 54 bits.
MIN_N_BITS = 50


# ==================================================================================================
#  MCTuplesSize
# ==================================================================================================
class MCTuplesSize(IntEnum):
    """`MCTuplesSize` is 1 of the sizes of the shipped Monte Carlo tuple set.

    Each size is a prefix of the next, so a smaller size's tuples are a subset of every larger size's.
    Members compare and compute as plain ints, so `MCTuplesSize(size)` both checks an int size and
    returns it as a member.
    """

    SIZE_32 = 32
    SIZE_64 = 64
    SIZE_128 = 128
    SIZE_256 = 256
    SIZE_512 = 512
    SIZE_1024 = 1024

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        """Raise `ValueError` listing the sizes, for a `value` that is not 1 of them."""
        raise ValueError(f"A Monte Carlo tuple set size must be one of {[int(size) for size in cls]} (got {value!r}).")

    @property
    def size_below(self) -> "MCTuplesSize | None":
        """Return the next smaller size, half as large, which this size includes; None for the smallest size."""
        return None if self == min(MCTuplesSize) else MCTuplesSize(self // 2)

    @property
    def n_required(self) -> int:
        """Return the number of tuples that this size takes from the size below; 0 for the smallest size."""
        return 0 if self.size_below is None else int(self.size_below)

    @property
    def n_new(self) -> int:
        """Return the number of tuples that this size adds to the size below; the smallest size adds all its tuples."""
        return int(self) - self.n_required

    @classmethod
    def up_to(cls, max_size: int) -> tuple["MCTuplesSize", ...]:
        """Return every size up to `max_size`, the smallest first.

        Raises:
            ValueError: If `max_size` is not 1 of the sizes.
        """
        largest = cls(max_size)
        return tuple(size for size in cls if size <= largest)


# ==================================================================================================
#  Fine lanes
# ==================================================================================================
# The construction cuts each axis into as many equal fine lanes as the largest size holds tuples, and no 2 tuples of
# the set share a fine lane, so the largest size holds exactly 1 tuple per fine lane on each axis.
N_FINE_LANES = int(max(MCTuplesSize))


def fine_lanes_of(values: np.ndarray) -> np.ndarray:
    """Return the fine lane of each value in [0, 1); fine lane `i` holds the values in `[i, i + 1) / N_FINE_LANES`."""
    return np.floor(values * N_FINE_LANES).astype(np.int64)


def fine_lane_edges_of(lanes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return the lower and the upper edge of each fine lane in `lanes`: the bounds of its values in `fine_lanes_of`."""
    return lanes / N_FINE_LANES, (lanes + 1) / N_FINE_LANES
