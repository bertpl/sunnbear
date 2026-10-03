"""`generate_mc_tuples` builds a nested set that holds exactly 1 tuple per lane at every size that it builds."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesConstructionError, construction, generate_mc_tuples
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid


@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_nested_sizes_with_1_tuple_per_lane():
    """A 1 s construction builds sizes 32 and 64; each holds 1 tuple per lane, and size 32 is the start of size 64.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0)

    # --- assert -----------------------
    assert tuples.size == 64
    assert LaneGrid.for_size(32, None).is_one_per_lane(tuples.first(32))
    assert LaneGrid.for_size(64, tuples.first(32)).is_one_per_lane(tuples)
    assert np.unique(tuples.u).size == np.unique(tuples.v).size == 64


def test_generate_mc_tuples_refuses_a_size_without_1_tuple_per_lane(monkeypatch):
    """A size whose tuples share a lane raises an error before the next size is built; the steps never produce one."""
    # --- arrange ----------------------
    monkeypatch.setattr(construction, "select_cells", lambda grid, *args: np.arange(grid.size))
    same_u_lane = MCTuples(np.full(32, 0.01), (np.arange(32) + 0.5) / 32)
    monkeypatch.setattr(construction, "refine_within_cells", lambda *args: same_u_lane)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="Size 32: the tuples do not hold exactly 1 per lane"):
        generate_mc_tuples(t_total_sec=1.0)
