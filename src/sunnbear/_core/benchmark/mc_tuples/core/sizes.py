"""`MCTuplesSize` lists the sizes in which the shipped Monte Carlo tuple set comes, and divides each size's square.

A size of `n` tuples divides the unit square in 2 ways:

- each axis into `n` equal LHS lanes, as in Latin hypercube sampling;
- the square into `sqrt(n)` by `sqrt(n)` equal tiles.

Each size of the shipped set holds exactly 1 tuple in each of its LHS lanes, along u and along v, and exactly 1 in each
of its tiles; `MCTuplesSize.check_lhs_lanes_and_tiles` checks a size's tuples for both.

The construction gives each value at least `MIN_N_BITS` bits of information.
"""

import math
from enum import IntEnum
from typing import NoReturn

import numpy as np

# `MIN_N_BITS` is the fewest bits of information (`n_bits`) that the construction leaves in any u value or v value, so
# that no short binary, decimal or rational description reproduces a value exactly; a random float64 value holds about
# 51 to 54 bits.
MIN_N_BITS = 50


# ==================================================================================================
#  MCTuplesSize
# ==================================================================================================
class MCTuplesSize(IntEnum):
    """`MCTuplesSize` is 1 of the sizes of the shipped Monte Carlo tuple set, with its LHS lanes and tiles.

    Each size is a prefix of the next, so a smaller size's tuples are a subset of every larger size's.
    Members compare and compute as plain ints, so `MCTuplesSize(size)` both checks an int size and
    returns it as a member.

    A size of `n` tuples has:

    - `n` LHS lanes of width `1/n` along each axis; LHS lane `i` holds the values in `[i, i + 1) / n`;
    - an LHS cell where 1 LHS lane along u crosses 1 LHS lane along v;
    - `sqrt(n)` by `sqrt(n)` tiles, each where 1 of `sqrt(n)` equal tile columns along u crosses 1 of as many equal
      tile rows along v; a tile holds `sqrt(n)` by `sqrt(n)` LHS cells.

    Every size is a power of 4, so `sqrt(n)` is a whole number, and each LHS lane and each tile of a size holds 4 LHS
    lanes and 2 by 2 tiles of the next size.
    """

    SIZE_4 = 4
    SIZE_16 = 16
    SIZE_64 = 64
    SIZE_256 = 256
    SIZE_1024 = 1024

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        """Raise `ValueError` listing the sizes, for a `value` that is not 1 of them."""
        raise ValueError(f"A Monte Carlo tuple set size must be one of {[int(size) for size in cls]} (got {value!r}).")

    # --------------------------------------------------------------------------
    #  Nesting
    # --------------------------------------------------------------------------
    @property
    def size_below(self) -> "MCTuplesSize | None":
        """Return the next smaller size, a quarter as large, which this size includes; None for the smallest size."""
        if self == min(MCTuplesSize):
            return None
        else:
            return MCTuplesSize(self // 4)

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

    # --------------------------------------------------------------------------
    #  LHS lanes
    # --------------------------------------------------------------------------
    @property
    def n_lower_half_lhs_lanes(self) -> int:
        """Return the number of LHS lanes of [0, 0.5] along each axis, half of the size's LHS lanes."""
        return int(self) // 2

    def lhs_lane_indices(self, values: np.ndarray) -> np.ndarray:
        """Return the index of each value's LHS lane; LHS lane `i` holds the values in `[i, i + 1) / size`."""
        return np.floor(values * int(self)).astype(np.int64)

    def lhs_lane_edges(self, lane_indices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return the lower and the upper edges of the LHS lanes in `lane_indices`.

        `lhs_lane_indices` puts a value in LHS lane `i` when it lies in `[lower, upper)` of that lane.
        """
        return lane_indices / int(self), (lane_indices + 1) / int(self)

    # --------------------------------------------------------------------------
    #  Tiles
    # --------------------------------------------------------------------------
    @property
    def n_tiles_per_axis(self) -> int:
        """Return the number of tile columns along u, which equals the number of tile rows along v: `sqrt(size)`."""
        return math.isqrt(int(self))

    def tile_indices(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Return the index of each tuple's tile, `column * n_tiles_per_axis + row`.

        Tile column `column` holds the u values in `[column, column + 1) / n_tiles_per_axis`, and tile row `row` holds
        the v values in `[row, row + 1) / n_tiles_per_axis`.
        """
        columns = np.floor(u * self.n_tiles_per_axis).astype(np.int64)
        rows = np.floor(v * self.n_tiles_per_axis).astype(np.int64)
        return columns * self.n_tiles_per_axis + rows

    # --------------------------------------------------------------------------
    #  Check of a size's tuples
    # --------------------------------------------------------------------------
    def check_lhs_lanes_and_tiles(self, tuple_array: np.ndarray) -> None:
        """Raise `ValueError` unless each LHS lane along u, each LHS lane along v and each tile holds exactly 1 tuple.

        `tuple_array` is an `(n, 2)` array of (u, v) values in the open unit square, so it passes only when it holds
        exactly `size` tuples.

        Raises:
            ValueError: If an LHS lane or a tile holds no tuple, or 2 or more.
        """
        u, v = tuple_array[:, 0], tuple_array[:, 1]
        indices_per_part = {
            "LHS lanes along u": self.lhs_lane_indices(u),
            "LHS lanes along v": self.lhs_lane_indices(v),
            "Tiles": self.tile_indices(u, v),
        }
        for part, indices in indices_per_part.items():
            counts = np.bincount(indices, minlength=int(self))
            if not np.array_equal(counts, np.ones(int(self))):
                n_off = int((counts != 1).sum())
                raise ValueError(f"{part} that do not hold exactly 1 tuple: {n_off} of {int(self)}.")
