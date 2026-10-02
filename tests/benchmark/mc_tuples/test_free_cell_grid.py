"""`FreeCellGrid` finds the free bands, numbers the cells, samples inside them, and checks a Latin hypercube."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.benchmark.mc_tuples.free_cell_grid import FreeCellGrid

# A Latin hypercube of 4 tuples, 1 per band of width 1/4 on each axis; at size 8 it occupies bands 1, 2, 5 and 6
# along u, and bands 6, 0, 3 and 4 along v.
_SIZE_4 = MCTuples([0.15, 0.3, 0.7, 0.8], [0.8, 0.05, 0.45, 0.55])


def test_the_smallest_size_has_every_band_free():
    """Without a size below, every band of each axis is free, and the grid has size x size cells."""
    # --- act --------------------------
    grid = FreeCellGrid.for_size(4, None)

    # --- assert -----------------------
    assert grid.free_u_bands.tolist() == [0, 1, 2, 3]
    assert grid.free_v_bands.tolist() == [0, 1, 2, 3]
    assert grid.n_cells == 16


def test_a_nested_size_has_the_bands_free_that_the_size_below_leaves_empty():
    """At size 8, the 4 tuples of size 4 leave 4 bands free on each axis, crossing in 16 cells."""
    # --- act --------------------------
    grid = FreeCellGrid.for_size(8, _SIZE_4)

    # --- assert -----------------------
    assert grid.free_u_bands.tolist() == [0, 3, 4, 7]
    assert grid.free_v_bands.tolist() == [1, 2, 5, 7]
    assert grid.n_cells == 16
    assert grid.cell_centers[[0, 1, 4]].tolist() == [[0.5 / 8, 1.5 / 8], [0.5 / 8, 2.5 / 8], [3.5 / 8, 1.5 / 8]]


def test_random_latin_hypercube_cells_pair_each_free_u_band_with_1_free_v_band():
    """The random cells hold 1 cell per free u band and 1 per free v band."""
    # --- arrange ----------------------
    grid = FreeCellGrid.for_size(8, _SIZE_4)

    # --- act --------------------------
    cells = grid.random_latin_hypercube_cells(np.random.default_rng(0))

    # --- assert -----------------------
    assert grid.is_one_per_free_band(cells)
    assert not grid.is_one_per_free_band(np.array([0, 1, 2, 3]))  # 4 cells of the first free u band


def test_samples_lie_strictly_inside_their_cells():
    """Every sample of a cell lies in that cell's bands on both axes, and above 0."""
    # --- arrange ----------------------
    grid = FreeCellGrid.for_size(8, _SIZE_4)
    cells = np.array([0, 5, 15])

    # --- act --------------------------
    samples = grid.sample_in_cells(cells, 50, np.random.default_rng(3))

    # --- assert -----------------------
    cell_bands = (grid.cell_centers[cells] * 8).astype(np.int64)
    assert samples.shape == (3, 50, 2)
    assert (FreeCellGrid.band_indices(samples, 8) == cell_bands[:, None, :]).all()
    assert (samples > 0).all()


@pytest.mark.parametrize(
    "tuples, is_latin_hypercube",
    [
        (_SIZE_4, True),
        (MCTuples([0.15, 0.2, 0.7, 0.8], [0.8, 0.05, 0.45, 0.55]), False),  # 2 u values in the first band
        (MCTuples([0.15, 0.3, 0.7, 0.8], [0.8, 0.05, 0.45, 0.95]), False),  # 2 v values in the last band
    ],
)
def test_is_latin_hypercube_requires_exactly_1_tuple_per_band_on_each_axis(tuples, is_latin_hypercube):
    """A set is a Latin hypercube only when every band along u and along v holds exactly 1 tuple."""
    # --- act / assert -----------------
    assert FreeCellGrid.is_latin_hypercube(tuples) == is_latin_hypercube
