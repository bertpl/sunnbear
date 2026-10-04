"""`LaneGrid` holds the lanes and cells for the new tuples of 1 size of the tuple set.

The tuple set is nested: each size includes the size below it, which is half as large. Each axis of a size gets:

- **new values**, 1 per new tuple, assigned to the gaps between the values of the size below
  (`LaneGrid.assign_new_values`);
- **lanes** whose boundaries lie halfway between consecutive values, old and new (`LaneGrid.lane_boundaries`).

Every value lies in its own lane. A new lane is the lane of a new value, and a cell is the crossing of a new u lane
and a new v lane; once each new tuple lies inside its own cell, the size holds exactly 1 tuple per lane along u
and along v.

The lanes belong to 1 size only: the next size assigns its own new values to the gaps between all of this size's
values and cuts its own lanes.
"""

from dataclasses import dataclass
from typing import Self

import numpy as np

from .sizes import MCTuplesSize
from .tuples import MCTuples


# ==================================================================================================
#  LaneGrid
# ==================================================================================================
@dataclass(frozen=True)
class LaneGrid:
    """`LaneGrid` holds, for 1 size of the tuple set, the new values per axis and the lanes cut around them.

    The cells are the crossings of a new u lane and a new v lane, numbered row by row: cell `i * n_new + j`
    crosses the lane of `new_u_values[i]` and the lane of `new_v_values[j]`.

    Attributes:
        size: The number of tuples of the size.
        required_tuples: The tuples of the size below, which the size includes; None for the smallest size.
        new_u_values: The new values along u, ascending; `new_u_values[i]` is the u coordinate of the cells of row `i`.
        new_v_values: The new values along v, ascending.
        new_u_lanes: The lower and upper boundary of each new u lane, as an `(n_new, 2)` array in the order of
            `new_u_values`.
        new_v_lanes: The lower and upper boundary of each new v lane, in the order of `new_v_values`.
    """

    size: int
    required_tuples: MCTuples | None
    new_u_values: np.ndarray
    new_v_values: np.ndarray
    new_u_lanes: np.ndarray
    new_v_lanes: np.ndarray

    @classmethod
    def for_size(cls, size: int, required_tuples: MCTuples | None) -> Self:
        """Return the grid for `size`, given `required_tuples`, the tuples of the size below (None at the smallest)."""
        required_tuple_array = cls._tuple_array_or_empty(required_tuples)
        new_values_per_axis, new_lanes_per_axis = [], []
        for axis in range(2):
            new_values = cls.assign_new_values(required_tuple_array[:, axis], size)
            all_values = np.sort(np.concatenate([required_tuple_array[:, axis], new_values]))
            boundaries = cls.lane_boundaries(all_values)
            lane_indices = np.searchsorted(all_values, new_values)
            new_values_per_axis.append(new_values)
            new_lanes_per_axis.append(np.column_stack([boundaries[lane_indices], boundaries[lane_indices + 1]]))
        return cls(size, required_tuples, *new_values_per_axis, *new_lanes_per_axis)

    # --------------------------------------------------------------------------
    #  Values and lanes of 1 axis
    # --------------------------------------------------------------------------
    @staticmethod
    def assign_new_values(old_values: np.ndarray, size: int) -> np.ndarray:
        """Return the new values of 1 axis, ascending, placed in the gaps between the sorted `old_values`.

        The sorted old values cut [0, 1] into gaps. Each of the `size - len(old_values)` new values goes, one at a
        time, to the gap that, once its values are evenly spaced, would leave the widest spacing after adding it,
        which maximizes the smallest gap along the axis.

        Within a gap, the values are evenly spaced (`space_values_in_gaps`); with no old values, the new values
        are `i / (size - 1)`.
        """
        n_new = size - old_values.size
        if old_values.size == 0:
            return np.linspace(0.0, 1.0, n_new)
        bounds = np.concatenate([[0.0], np.sort(old_values), [1.0]])
        widths = np.diff(bounds)
        is_edge_gap = np.zeros(widths.size, dtype=bool)
        is_edge_gap[[0, -1]] = True
        counts = np.zeros(widths.size, dtype=np.int64)
        for _ in range(n_new):
            sub_gap_after_addition = widths / np.where(is_edge_gap, counts + 1, counts + 2)
            counts[np.argmax(sub_gap_after_addition)] += 1
        return LaneGrid.space_values_in_gaps(bounds, counts)

    @staticmethod
    def space_values_in_gaps(bounds: np.ndarray, counts: np.ndarray) -> np.ndarray:
        """Return `counts[g]` evenly spaced values in each gap `g` between consecutive `bounds`, ascending.

        An interior gap of width `w` with `m` values has sub-gaps `w / (m + 1)`; the first and the last gap put
        their outermost value at `bounds[0]` and `bounds[-1]`, so their sub-gaps are `w / m`.
        """
        values = []
        for gap, (lo, hi, m) in enumerate(zip(bounds[:-1], bounds[1:], counts, strict=True)):
            if m == 0:
                continue
            if gap == 0:
                values.append(lo + np.arange(m) * (hi - lo) / m)
            elif gap == counts.size - 1:
                values.append(lo + np.arange(1, m + 1) * (hi - lo) / m)
            else:
                values.append(lo + np.arange(1, m + 1) * (hi - lo) / (m + 1))
        return np.concatenate(values)

    @staticmethod
    def lane_boundaries(values: np.ndarray) -> np.ndarray:
        """Return `len(values) + 1` lane boundaries: 0, one halfway between each 2 sorted neighbors, and 1."""
        values = np.sort(values)
        return np.concatenate([[0.0], (values[:-1] + values[1:]) / 2, [1.0]])

    # --------------------------------------------------------------------------
    #  Required tuples
    # --------------------------------------------------------------------------
    @property
    def required_tuple_array(self) -> np.ndarray:
        """Return the required tuples as an `(n, 2)` array of (u, v) values; empty for the smallest size."""
        return self._tuple_array_or_empty(self.required_tuples)

    # --------------------------------------------------------------------------
    #  Cells
    # --------------------------------------------------------------------------
    @property
    def n_new(self) -> int:
        """Return the number of new tuples, which is also the number of new lanes per axis."""
        return self.new_u_values.size

    @property
    def n_cells(self) -> int:
        """Return the number of cells, `n_new` squared."""
        return self.n_new * self.n_new

    @property
    def cell_tuple_array(self) -> np.ndarray:
        """Return the tuple (new u value, new v value) of every cell, as an `(n_cells, 2)` array, row by row."""
        return np.column_stack([np.repeat(self.new_u_values, self.n_new), np.tile(self.new_v_values, self.n_new)])

    def required_and_cell_tuple_array(self, cells: np.ndarray) -> np.ndarray:
        """Return the required tuples, then the tuples of `cells`, as a `(size, 2)` array of (u, v) values."""
        return np.vstack([self.required_tuple_array, self.cell_tuple_array[cells]])

    def lane_cells(self) -> list[np.ndarray]:
        """Return the cells of each new u lane, then the cells of each new v lane."""
        cells = np.arange(self.n_cells).reshape(self.n_new, self.n_new)
        return [*cells, *cells.T]

    def random_one_per_new_lane_cells(self, rng: np.random.Generator) -> np.ndarray:
        """Return random cells that pair each new u lane with a different new v lane, drawn with `rng`."""
        return np.arange(self.n_new) * self.n_new + rng.permutation(self.n_new)

    def is_one_per_new_lane(self, cells: np.ndarray) -> bool:
        """Return whether `cells` holds exactly 1 cell per new u lane and 1 per new v lane."""
        rows, columns = np.divmod(cells, self.n_new)
        return np.unique(rows).size == np.unique(columns).size == cells.size == self.n_new

    def sample_in_cells(self, cells: np.ndarray, n_per_cell: int, rng: np.random.Generator) -> np.ndarray:
        """Return `n_per_cell` uniform random tuples inside each of `cells`, as an `(len(cells), n_per_cell, 2)` array.

        Every tuple lies strictly inside its cell, so also strictly inside the unit square: a draw that rounds
        onto a lane boundary is drawn again.
        """
        rows, columns = np.divmod(cells, self.n_new)
        lo = np.column_stack([self.new_u_lanes[rows, 0], self.new_v_lanes[columns, 0]])[:, None, :]
        hi = np.column_stack([self.new_u_lanes[rows, 1], self.new_v_lanes[columns, 1]])[:, None, :]
        samples = np.empty((cells.size, n_per_cell, 2))
        needs_redraw = np.ones(samples.shape, dtype=bool)
        while needs_redraw.any():
            draws = lo + rng.random(samples.shape) * (hi - lo)
            samples[needs_redraw] = draws[needs_redraw]
            needs_redraw = (samples <= lo) | (samples >= hi)
        return samples

    # --------------------------------------------------------------------------
    #  Lanes of the whole size
    # --------------------------------------------------------------------------
    def is_one_per_lane(self, tuples: MCTuples) -> bool:
        """Return whether each lane of the size, along u and along v, holds exactly 1 of `tuples`.

        `tuples` is the whole size, the size below included; its lane boundaries lie halfway between consecutive
        values, the values of the size below and the new values of this grid together.
        """
        if tuples.size != self.size:
            return False
        for axis, new_values in ((0, self.new_u_values), (1, self.new_v_values)):
            boundaries = self.lane_boundaries(np.concatenate([self.required_tuple_array[:, axis], new_values]))
            lane_indices = np.searchsorted(boundaries[1:-1], tuples.tuple_array[:, axis], side="right")
            if not (np.bincount(lane_indices, minlength=self.size) == 1).all():
                return False
        return True

    @classmethod
    def is_one_per_lane_on_rebuilt_grid(cls, tuples: MCTuples) -> bool:
        """Return whether `tuples`, 1 size of the nested set, holds exactly 1 tuple per lane along u and along v.

        The grid of the size is rebuilt from the tuples of the size below, the first half of `tuples`.

        Raises:
            ValueError: If `tuples.size` is not 1 of `MCTuplesSize`.
        """
        size_below = MCTuplesSize(tuples.size).size_below
        required_tuples = None if size_below is None else tuples.first(size_below)
        return cls.for_size(tuples.size, required_tuples).is_one_per_lane(tuples)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _tuple_array_or_empty(tuples: MCTuples | None) -> np.ndarray:
        """Return `tuples` as an `(n, 2)` array of (u, v) values; empty when `tuples` is None."""
        return np.empty((0, 2)) if tuples is None else tuples.tuple_array
