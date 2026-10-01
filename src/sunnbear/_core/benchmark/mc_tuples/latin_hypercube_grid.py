"""`LatinHypercubeGrid` holds the grid cells in which 1 size of the tuple set places its new tuples.

A set of `size` tuples is a Latin hypercube when each of the `size` equal bands of [0, 1) along u, and
each along v, holds exactly 1 tuple. The tuple set is nested: each size includes the size below it, whose
tuples already occupy half of the bands. The new tuples of a size go in the cells where a free band along u
crosses a free band along v, 1 per free band on each axis, so the size is again a Latin hypercube.
"""

from dataclasses import dataclass
from typing import Self

import numpy as np

from .tuples import MCTuples


# ==================================================================================================
#  LatinHypercubeGrid
# ==================================================================================================
@dataclass(frozen=True)
class LatinHypercubeGrid:
    """`LatinHypercubeGrid` is the grid of 1 size: the bands along u and along v that hold no tuple of the size below.

    The cells are the crossings of a free u band and a free v band, numbered row by row: cell
    `i * len(free_v_bands) + j` crosses the free u band `free_u_bands[i]` and the free v band `free_v_bands[j]`.

    Attributes:
        size: The number of tuples of the size, which is also the number of bands per axis.
        free_u_bands: The indices of the u bands that hold no tuple of the size below, ascending.
        free_v_bands: The indices of the v bands that hold no tuple of the size below, ascending.
    """

    size: int
    free_u_bands: np.ndarray
    free_v_bands: np.ndarray

    @classmethod
    def for_size(cls, size: int, required: MCTuples | None) -> Self:
        """Return the grid of `size`, whose tuples include `required`, the size below it (None for the smallest size)."""
        if required is None:
            return cls(size, np.arange(size), np.arange(size))
        return cls(
            size,
            np.setdiff1d(np.arange(size), cls.band_indices(required.u, size)),
            np.setdiff1d(np.arange(size), cls.band_indices(required.v, size)),
        )

    # --------------------------------------------------------------------------
    #  Cells
    # --------------------------------------------------------------------------
    @property
    def n_cells(self) -> int:
        """Return the number of cells, the number of free u bands times the number of free v bands."""
        return self.free_u_bands.size * self.free_v_bands.size

    @property
    def cell_centers(self) -> np.ndarray:
        """Return the center of every cell, as an `(n_cells, 2)` array of (u, v) values."""
        return (
            np.column_stack([self._cell_u_bands(), self._cell_v_bands()]).astype(np.float64) / self.size
            + 0.5 / self.size
        )

    def latin_hypercube_cells(self, permutation: np.ndarray) -> np.ndarray:
        """Return the cells that pair free u band `i` with free v band `permutation[i]`, 1 per free band on each axis."""
        return np.arange(self.free_u_bands.size) * self.free_v_bands.size + permutation

    def sample_in_cells(self, cells: np.ndarray, n_per_cell: int, rng: np.random.Generator) -> np.ndarray:
        """Return `n_per_cell` uniform random tuples inside each of `cells`, as an `(len(cells), n_per_cell, 2)` array.

        Every tuple lies strictly inside its cell's bands, as `band_indices` computes them: a draw that rounds
        onto a band edge, or onto 0, is drawn again.
        """
        lower_bands = np.column_stack([self._cell_u_bands()[cells], self._cell_v_bands()[cells]])[:, None, :]
        samples = np.empty((cells.size, n_per_cell, 2))
        is_redraw = np.ones(samples.shape, dtype=bool)
        while is_redraw.any():
            draws = (lower_bands + rng.random(samples.shape)) / self.size
            samples[is_redraw] = draws[is_redraw]
            is_redraw = (self.band_indices(samples, self.size) != lower_bands) | (samples <= 0.0)
        return samples

    # --------------------------------------------------------------------------
    #  Bands
    # --------------------------------------------------------------------------
    @staticmethod
    def band_indices(values: np.ndarray, size: int) -> np.ndarray:
        """Return, per value in [0, 1), the index of the band of width `1/size` that holds it."""
        return np.minimum((np.asarray(values) * size).astype(np.int64), size - 1)

    @classmethod
    def is_latin_hypercube(cls, tuples: MCTuples) -> bool:
        """Return whether each of the `tuples.size` bands along u, and each along v, holds exactly 1 tuple."""
        return all(
            (np.bincount(cls.band_indices(values, tuples.size), minlength=tuples.size) == 1).all()
            for values in (tuples.u, tuples.v)
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _cell_u_bands(self) -> np.ndarray:
        """Return the u band of every cell, row by row."""
        return np.repeat(self.free_u_bands, self.free_v_bands.size)

    def _cell_v_bands(self) -> np.ndarray:
        """Return the v band of every cell, row by row."""
        return np.tile(self.free_v_bands, self.free_u_bands.size)
