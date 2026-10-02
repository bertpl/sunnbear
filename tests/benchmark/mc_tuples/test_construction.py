"""`generate_mc_tuples` builds a nested set that is a Latin hypercube at every size that it builds."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesConstructionError, construction, generate_mc_tuples
from sunnbear._core.benchmark.mc_tuples.free_cell_grid import FreeCellGrid


@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_nested_latin_hypercubes():
    """A 1 s construction builds sizes 32 and 64; each is a Latin hypercube, and size 32 is the start of size 64.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0)

    # --- assert -----------------------
    assert tuples.size == 64
    assert FreeCellGrid.is_latin_hypercube(tuples.first(32))
    assert FreeCellGrid.is_latin_hypercube(tuples)
    assert np.unique(tuples.u).size == np.unique(tuples.v).size == 64


def test_generate_mc_tuples_refuses_a_size_that_is_not_a_latin_hypercube(monkeypatch):
    """A size whose tuples share a band raises an error before the next size is built; the steps never produce one."""
    # --- arrange ----------------------
    monkeypatch.setattr(construction, "select_cells", lambda grid, *args: np.arange(grid.size))
    same_u_band = MCTuples(np.full(32, 0.01), (np.arange(32) + 0.5) / 32)
    monkeypatch.setattr(construction, "refine_within_cells", lambda *args: same_u_band)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="Size 32: the tuples are not a Latin hypercube"):
        generate_mc_tuples(t_total_sec=1.0)
