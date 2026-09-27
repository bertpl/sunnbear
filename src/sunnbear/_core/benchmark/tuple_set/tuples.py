"""`UvTuples` holds a set of (u, v) tuples, the dimensionless samples of every Monte Carlo benchmark run.

A tuple `(u, v)` lies in the open unit square. When the set is mapped onto one test function, `u` sets
the tolerance `xtol` log-uniformly between `xtol_min` and `2·xtol_min`, and `v` sets the parameter `c`
linearly between the function's `c_min` and `c_max`, so the same set works for every test function.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

# The shipped set comes in these sizes; each is a prefix of the next, so a smaller size's tuples are a
# subset of every larger size's.
UV_TUPLES_SIZES = (32, 64, 128, 256, 512, 1024)

# Each axis is cut into this many equal spans; `UvTuplesStats` counts the tuples per span, and the
# construction keeps each count within 1 of `size / N_SPANS`.
N_SPANS = 8


# ==================================================================================================
#  UvTuples
# ==================================================================================================
class UvTuples:
    """`UvTuples` is a set of (u, v) tuples in the open unit square, stored as 2 read-only arrays."""

    def __init__(self, u: ArrayLike, v: ArrayLike) -> None:
        """Store copies of `u` and `v` as read-only float64 arrays.

        Raises:
            ValueError: If `u` and `v` are not 1-D arrays of the same length, hold fewer than 2
                tuples, or hold a value outside the open interval (0, 1).
        """
        u_array = np.array(u, dtype=np.float64)
        v_array = np.array(v, dtype=np.float64)
        if u_array.ndim != 1 or u_array.shape != v_array.shape:
            raise ValueError(
                f"u and v must be 1-D arrays of equal length (got shapes {u_array.shape}, {v_array.shape})."
            )
        if u_array.size < 2:
            raise ValueError(f"A tuple set holds at least 2 tuples (got {u_array.size}).")
        if not (np.all((u_array > 0) & (u_array < 1)) and np.all((v_array > 0) & (v_array < 1))):
            raise ValueError("Every u and v value must lie in the open interval (0, 1).")
        u_array.setflags(write=False)
        v_array.setflags(write=False)
        self._u = u_array
        self._v = v_array

    # --------------------------------------------------------------------------
    #  Values
    # --------------------------------------------------------------------------
    @property
    def u(self) -> np.ndarray:
        """Return the u values, read-only."""
        return self._u

    @property
    def v(self) -> np.ndarray:
        """Return the v values, read-only."""
        return self._v

    @property
    def size(self) -> int:
        """Return the number of tuples."""
        return self._u.size

    def first(self, size: int) -> "UvTuples":
        """Return the first `size` tuples.

        Raises:
            ValueError: If `size` is below 2 or above this set's size.
        """
        if not 2 <= size <= self.size:
            raise ValueError(f"size must lie in [2, {self.size}] (got {size}).")
        return UvTuples(self._u[:size], self._v[:size])

    # --------------------------------------------------------------------------
    #  Mapping onto a test function
    # --------------------------------------------------------------------------
    def to_xtol_and_c(self, xtol_min: float, c_min: float, c_max: float) -> tuple[np.ndarray, np.ndarray]:
        """Return the `(xtol, c)` value of every tuple for one test function.

        The mapping is `xtol = xtol_min · 2^u` and `c = c_min + v · (c_max - c_min)`, so `xtol` is
        log-uniform within `(xtol_min, 2·xtol_min)` and `c` is uniform within `(c_min, c_max)`.

        Returns:
            The `xtol` array and the `c` array, in tuple order.
        """
        return xtol_min * np.exp2(self._u), c_min + self._v * (c_max - c_min)

    # --------------------------------------------------------------------------
    #  Spread
    # --------------------------------------------------------------------------
    def stats(self) -> "UvTuplesStats":
        """Return the set's span counts and its 3 min separations.

        The L2 min separation is computed from the full pairwise distance matrix, so memory grows with
        the square of the size.
        """
        points = np.column_stack([self._u, self._v])
        return UvTuplesStats(
            size=self.size,
            span_counts_u=_span_counts(self._u),
            span_counts_v=_span_counts(self._v),
            min_separation_l2=_min_separation_l2(points),
            min_separation_u=_min_separation_along_axis(self._u),
            min_separation_v=_min_separation_along_axis(self._v),
        )


# ==================================================================================================
#  UvTuplesStats
# ==================================================================================================
@dataclass(frozen=True)
class UvTuplesStats:
    """`UvTuplesStats` describes how evenly a tuple set is spread.

    Each min separation is the smallest distance between 2 tuples: in the square (L2), along u, or
    along v. Each `min_separation_*_fraction` property divides that min separation by the separation of
    `size` evenly spaced tuples:
    `1/(size - 1)` along an axis, and the spacing `1/(√size - 1)` of a square grid in L2.
    """

    size: int
    span_counts_u: tuple[int, ...]
    span_counts_v: tuple[int, ...]
    min_separation_l2: float
    min_separation_u: float
    min_separation_v: float

    @property
    def min_separation_l2_fraction(self) -> float:
        """Return the L2 min separation as a fraction of the grid spacing `1/(√size - 1)`."""
        return self.min_separation_l2 * (np.sqrt(self.size) - 1)

    @property
    def min_separation_u_fraction(self) -> float:
        """Return the min separation along u as a fraction of `1/(size - 1)`."""
        return self.min_separation_u * (self.size - 1)

    @property
    def min_separation_v_fraction(self) -> float:
        """Return the min separation along v as a fraction of `1/(size - 1)`."""
        return self.min_separation_v * (self.size - 1)

    @property
    def max_span_count_deviation(self) -> float:
        """Return the largest difference, over both axes, between a span's count and `size / N_SPANS`."""
        counts = np.array(self.span_counts_u + self.span_counts_v)
        return float(np.abs(counts - self.size / N_SPANS).max())


# ==================================================================================================
#  Helpers
# ==================================================================================================
def span_indices(values: np.ndarray) -> np.ndarray:
    """Return the index of the span, among `N_SPANS` equal spans of (0, 1), that holds each value."""
    return np.minimum((values * N_SPANS).astype(np.int64), N_SPANS - 1)


def _span_counts(values: np.ndarray) -> tuple[int, ...]:
    """Return the number of values in each of the `N_SPANS` spans of (0, 1)."""
    return tuple(int(n) for n in np.bincount(span_indices(values), minlength=N_SPANS))


def _min_separation_along_axis(values: np.ndarray) -> float:
    """Return the smallest difference between 2 of the values."""
    return float(np.diff(np.sort(values)).min())


def _min_separation_l2(points: np.ndarray) -> float:
    """Return the smallest L2 distance between 2 of the points, from the full distance matrix."""
    diff = points[:, None, :] - points[None, :, :]
    distances = np.sqrt((diff**2).sum(axis=-1))
    np.fill_diagonal(distances, np.inf)
    return float(distances.min())
