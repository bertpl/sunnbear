"""`MCTuples` holds a set of (u, v) tuples, the dimensionless samples of every Monte Carlo benchmark run.

A tuple `(u, v)` lies in the open unit square. When the set is mapped onto one test function, `u` sets
the tolerance `xtol` log-uniformly between `xtol_min` and `2·xtol_min`, and `v` sets the parameter `c`
linearly between the function's `c_min` and `c_max`, so the same set works for every test function.
"""

from functools import cached_property

import numpy as np
from numpy.typing import ArrayLike

from sunnbear._core.stats import gpq

# The level of the geometric pseudo-quantile (`gpq`) that the construction maximizes and `MCTuplesStats` reports. At
# 0.1 the gpq is a soft minimum: the smallest separations dominate it, but not the single smallest alone.
GPQ_LEVEL = 0.1


# ==================================================================================================
#  MCTuples
# ==================================================================================================
class MCTuples:
    """`MCTuples` is a set of Monte Carlo (u, v) tuples in the open unit square, stored as 2 read-only arrays."""

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

    @property
    def tuple_array(self) -> np.ndarray:
        """Return the tuples as a `(size, 2)` array of (u, v) values."""
        return np.column_stack([self._u, self._v])

    def first(self, size: int) -> "MCTuples":
        """Return the first `size` tuples.

        Raises:
            ValueError: If `size` is below 2 or above this set's size.
        """
        if not 2 <= size <= self.size:
            raise ValueError(f"size must lie in [2, {self.size}] (got {size}).")
        return MCTuples(self._u[:size], self._v[:size])

    def extended_by(self, other: "MCTuples") -> "MCTuples":
        """Return this set followed by the tuples of `other`."""
        return MCTuples(np.concatenate([self._u, other.u]), np.concatenate([self._v, other.v]))

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
    def stats(self) -> "MCTuplesStats":
        """Return the set's spread statistics, each computed when first read."""
        return MCTuplesStats(self.tuple_array)


# ==================================================================================================
#  MCTuplesStats
# ==================================================================================================
class MCTuplesStats:
    """`MCTuplesStats` describes how evenly (u, v) tuples are spread; each statistic is computed when first read.

    Each tuple's separation is its distance to its nearest other tuple: in the square (L2), along u, or along v.
    The separations of each kind are summarized by 2 statistics:

    - the min separation, the smallest of them;
    - gpq(0.1), the geometric pseudo-quantile at `GPQ_LEVEL`, which the construction maximizes.

    Each `*_fraction` property divides its statistic by the separation of `size` evenly spaced tuples: `1/(size - 1)`
    along an axis, and the spacing `1/(√size - 1)` of a square grid in L2. `score` combines the 3 gpq fractions into
    1 number by which tuple sets are compared.

    `MCTuplesStats` takes an `(n, 2)` array, not an `MCTuples`, so that a caller that holds tuples only as an array,
    such as a size's tuples before the mean correction, does not have to build an `MCTuples` first.
    """

    def __init__(self, tuple_array: ArrayLike) -> None:
        """Store `tuple_array`, an `(n, 2)` array of (u, v) values."""
        self._tuple_array = np.asarray(tuple_array, dtype=np.float64)

    @property
    def size(self) -> int:
        """Return the number of tuples."""
        return self._tuple_array.shape[0]

    # --------------------------------------------------------------------------
    #  Min separations
    # --------------------------------------------------------------------------
    @property
    def min_separation_l2(self) -> float:
        """Return the smallest L2 distance between 2 tuples."""
        return float(self._separations_l2.min())

    @property
    def min_separation_u(self) -> float:
        """Return the smallest difference between 2 u values."""
        return float(self._separations_u.min())

    @property
    def min_separation_v(self) -> float:
        """Return the smallest difference between 2 v values."""
        return float(self._separations_v.min())

    @property
    def min_separation_l2_fraction(self) -> float:
        """Return the L2 min separation as a fraction of the grid spacing `1/(√size - 1)`."""
        return self.min_separation_l2 * (float(np.sqrt(self.size)) - 1.0)

    @property
    def min_separation_u_fraction(self) -> float:
        """Return the min separation along u as a fraction of `1/(size - 1)`."""
        return self.min_separation_u * (self.size - 1.0)

    @property
    def min_separation_v_fraction(self) -> float:
        """Return the min separation along v as a fraction of `1/(size - 1)`."""
        return self.min_separation_v * (self.size - 1.0)

    # --------------------------------------------------------------------------
    #  gpq of the separations
    # --------------------------------------------------------------------------
    @cached_property
    def gpq_l2_fraction(self) -> float:
        """Return the gpq at `GPQ_LEVEL` of the L2 separations as a fraction of the grid spacing `1/(√size - 1)`."""
        return gpq(self._separations_l2, GPQ_LEVEL) * (float(np.sqrt(self.size)) - 1.0)

    @cached_property
    def gpq_u_fraction(self) -> float:
        """Return the gpq at `GPQ_LEVEL` of the separations along u as a fraction of `1/(size - 1)`."""
        return gpq(self._separations_u, GPQ_LEVEL) * (self.size - 1.0)

    @cached_property
    def gpq_v_fraction(self) -> float:
        """Return the gpq at `GPQ_LEVEL` of the separations along v as a fraction of `1/(size - 1)`."""
        return gpq(self._separations_v, GPQ_LEVEL) * (self.size - 1.0)

    @property
    def score(self) -> float:
        """Return `(u · v · L2²)^(1/4)` of the 3 gpq fractions: their geomean with weights 1, 1 and 2.

        The weight 2 on L2 matches the construction's objective, which takes gpq over squared L2 distances, and
        gpq(d²) = gpq(d)².
        """
        return (self.gpq_u_fraction * self.gpq_v_fraction * self.gpq_l2_fraction**2) ** 0.25

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @cached_property
    def _separations_l2(self) -> np.ndarray:
        """Return each tuple's L2 distance to its nearest other tuple.

        It is computed from the full pairwise distance matrix, so memory grows with the square of the size.
        """
        tuple_array = self._tuple_array
        diff = tuple_array[:, None, :] - tuple_array[None, :, :]
        distances = np.sqrt((diff**2).sum(axis=-1))
        np.fill_diagonal(distances, np.inf)
        return distances.min(axis=1)

    @cached_property
    def _separations_u(self) -> np.ndarray:
        """Return each tuple's distance along u to its nearest other tuple."""
        return self._separations_along_axis(self._tuple_array[:, 0])

    @cached_property
    def _separations_v(self) -> np.ndarray:
        """Return each tuple's distance along v to its nearest other tuple."""
        return self._separations_along_axis(self._tuple_array[:, 1])

    @staticmethod
    def _separations_along_axis(values: np.ndarray) -> np.ndarray:
        """Return each value's distance to its nearest other value, in the values' order."""
        order = np.argsort(values)
        differences = np.diff(values[order])
        nearest_in_order = np.minimum(np.concatenate([[np.inf], differences]), np.concatenate([differences, [np.inf]]))
        separations = np.empty_like(nearest_in_order)
        separations[order] = nearest_in_order
        return separations
