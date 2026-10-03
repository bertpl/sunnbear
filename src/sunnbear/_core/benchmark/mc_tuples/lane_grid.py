"""`LaneGrid` holds the lanes and cells for the new tuples of 1 size of the tuple set.

The tuple set is nested: each size includes the size below it, which is half as large. The new tuples of a
size get new values along each axis, assigned to the gaps between the values of the size below
(`LaneGrid.assign_new_values`), and each axis is cut into lanes that meet at the midpoints between consecutive
values, old and new (`LaneGrid.lane_boundaries`). Every value lies in its own lane, so the size holds exactly
1 tuple per lane along u and along v once each new tuple stays inside its cell, the crossing of a new u lane
and a new v lane.

The lanes are a construction device of 1 size: the next size assigns its own new values to the gaps between
all of this size's values and cuts its own lanes.
"""

from dataclasses import dataclass
from typing import Self

import numpy as np

from .tuples import MCTuples


# ==================================================================================================
#  LaneGrid
# ==================================================================================================
@dataclass(frozen=True)
class LaneGrid:
    """`LaneGrid` holds, for 1 size of the tuple set, the new values per axis and the lanes cut around them.

    The cells are the crossings of a new u lane and a new v lane, numbered row by row: cell `i * n_new + j`
    crosses the lane of `u_values[i]` and the lane of `v_values[j]`.

    Attributes:
        size: The number of tuples of the size.
        required_tuples: The tuples of the size below, which the size includes; None for the smallest size.
        u_values: The new values along u, ascending; `u_values[i]` is the u coordinate of the cells of row `i`.
        v_values: The new values along v, ascending.
        u_lanes: The lower and upper boundary of each new u lane, as an `(n_new, 2)` array in the order of `u_values`.
        v_lanes: The lower and upper boundary of each new v lane, in the order of `v_values`.
    """

    size: int
    required_tuples: MCTuples | None
    u_values: np.ndarray
    v_values: np.ndarray
    u_lanes: np.ndarray
    v_lanes: np.ndarray

    @classmethod
    def for_size(cls, size: int, required_tuples: MCTuples | None) -> Self:
        """Return the grid for `size`, given `required_tuples`, the tuples of the size below (None at the smallest)."""
        required = np.empty((0, 2)) if required_tuples is None else required_tuples.points
        values, lanes = [], []
        for axis in range(2):
            new_values = cls.assign_new_values(required[:, axis], size)
            all_values = np.sort(np.concatenate([required[:, axis], new_values]))
            boundaries = cls.lane_boundaries(all_values)
            lane_index = np.searchsorted(all_values, new_values)
            values.append(new_values)
            lanes.append(np.column_stack([boundaries[lane_index], boundaries[lane_index + 1]]))
        return cls(size, required_tuples, values[0], values[1], lanes[0], lanes[1])

    # --------------------------------------------------------------------------
    #  Values and lanes of 1 axis
    # --------------------------------------------------------------------------
    @staticmethod
    def assign_new_values(old_values: np.ndarray, size: int) -> np.ndarray:
        """Return the new values of 1 axis, ascending, placed in the gaps between the sorted `old_values`.

        The sorted old values cut [0, 1] into gaps. Each of the `size - len(old_values)` new values goes, one at a
        time, to the gap whose sub-gaps after the addition stay the widest, which maximizes the smallest gap along
        the axis. Within a gap, the
        values are evenly spaced: an interior gap of width `g` with `m` values has sub-gaps `g / (m + 1)`; an
        edge gap puts its outermost value at 0 or 1, so its sub-gaps are `g / m`. With no old values, the new
        values are `i / (size - 1)`.
        """
        n_new = size - old_values.size
        if old_values.size == 0:
            return np.linspace(0.0, 1.0, n_new)

        # --- values per gap -------------------------
        bounds = np.concatenate([[0.0], np.sort(old_values), [1.0]])
        widths = np.diff(bounds)
        is_edge_gap = np.zeros(widths.size, dtype=bool)
        is_edge_gap[[0, -1]] = True
        counts = np.zeros(widths.size, dtype=np.int64)
        for _ in range(n_new):
            sub_gap_after_addition = widths / np.where(is_edge_gap, counts + 1, counts + 2)
            counts[np.argmax(sub_gap_after_addition)] += 1

        # --- positions within each gap --------------
        values = []
        for gap, (lo, hi, m) in enumerate(zip(bounds[:-1], bounds[1:], counts, strict=True)):
            if m == 0:
                continue
            if gap == 0:
                values.append(lo + np.arange(m) * (hi - lo) / m)
            elif gap == widths.size - 1:
                values.append(lo + np.arange(1, m + 1) * (hi - lo) / m)
            else:
                values.append(lo + np.arange(1, m + 1) * (hi - lo) / (m + 1))
        return np.concatenate(values)

    @staticmethod
    def lane_boundaries(values: np.ndarray) -> np.ndarray:
        """Return the `len(values) + 1` lane boundaries: 0, the midpoints between consecutive sorted values, and 1."""
        values = np.sort(values)
        return np.concatenate([[0.0], (values[:-1] + values[1:]) / 2, [1.0]])

    # --------------------------------------------------------------------------
    #  Required tuples
    # --------------------------------------------------------------------------
    @property
    def required_points(self) -> np.ndarray:
        """Return the required tuples as an `(n, 2)` array of (u, v) values; empty for the smallest size."""
        return np.empty((0, 2)) if self.required_tuples is None else self.required_tuples.points

    # --------------------------------------------------------------------------
    #  Cells
    # --------------------------------------------------------------------------
    @property
    def n_new(self) -> int:
        """Return the number of new tuples, which is also the number of new lanes per axis."""
        return self.u_values.size

    @property
    def n_cells(self) -> int:
        """Return the number of cells, `n_new` squared."""
        return self.n_new * self.n_new

    @property
    def cell_points(self) -> np.ndarray:
        """Return the point that represents every cell, (u value, v value), as an `(n_cells, 2)` array, row by row."""
        return np.column_stack([np.repeat(self.u_values, self.n_new), np.tile(self.v_values, self.n_new)])

    def lane_cells(self) -> list[np.ndarray]:
        """Return the cells of each new u lane, then the cells of each new v lane."""
        cells = np.arange(self.n_cells).reshape(self.n_new, self.n_new)
        return [*cells, *cells.T]

    def random_one_per_lane_cells(self, rng: np.random.Generator) -> np.ndarray:
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
        lo = np.column_stack([self.u_lanes[rows, 0], self.v_lanes[columns, 0]])[:, None, :]
        hi = np.column_stack([self.u_lanes[rows, 1], self.v_lanes[columns, 1]])[:, None, :]
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

        `tuples` is the whole size, the size below included; its lanes meet at the midpoints between the values
        of the size below and the new values of this grid.
        """
        if tuples.size != self.size:
            return False
        for axis, new_values in ((0, self.u_values), (1, self.v_values)):
            boundaries = self.lane_boundaries(np.concatenate([self.required_points[:, axis], new_values]))
            lane_index = np.searchsorted(boundaries[1:-1], tuples.points[:, axis], side="right")
            if not (np.bincount(lane_index, minlength=self.size) == 1).all():
                return False
        return True
