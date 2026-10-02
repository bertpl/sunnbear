"""`generate_mc_tuples` builds a nested set that is a Latin hypercube at every size it builds."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import generate_mc_tuples
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
