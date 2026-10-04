"""`generate_mc_tuples` builds a nested set with exactly 1 tuple per lane at every size, and reports each solve."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import (
    MCTuples,
    MCTuplesConstructionError,
    MCTuplesSolveReport,
    construction,
    generate_mc_tuples,
)
from sunnbear._core.benchmark.mc_tuples.construction_steps import MCTuplesConstructionStep
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid


@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_nested_sizes_with_1_tuple_per_lane_and_reports_each_solve():
    """A 1 s construction builds sizes 32 and 64, each with 1 tuple per lane, and reports its 4 solves in order.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- arrange ----------------------
    reports: list[MCTuplesSolveReport] = []

    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0, on_solve=reports.append)

    # --- assert -----------------------
    assert tuples.size == 64
    assert LaneGrid.is_one_per_lane_on_rebuilt_grid(tuples.first(32))
    assert LaneGrid.is_one_per_lane_on_rebuilt_grid(tuples)
    assert np.unique(tuples.u).size == np.unique(tuples.v).size == 64
    assert [(int(report.size), report.step) for report in reports] == [
        (32, MCTuplesConstructionStep.CELL_SELECTION),
        (32, MCTuplesConstructionStep.REFINEMENT),
        (64, MCTuplesConstructionStep.CELL_SELECTION),
        (64, MCTuplesConstructionStep.REFINEMENT),
    ]
    assert reports[0].points.shape == (32, 2)
    assert reports[-1].points.tolist() == tuples.points.tolist()
    assert all(report.stats().size == int(report.size) for report in reports)
    assert all(report.solution.score_checkpoints for report in reports)


def test_generate_mc_tuples_refuses_a_size_without_1_tuple_per_lane(monkeypatch):
    """A size whose tuples share a lane raises an error before the next size is built; the steps never produce one."""
    # --- arrange ----------------------
    monkeypatch.setattr(construction, "select_cells", lambda grid, *args: (np.arange(grid.size), None))
    same_u_lane = MCTuples(np.full(32, 0.01), (np.arange(32) + 0.5) / 32)
    monkeypatch.setattr(construction, "refine_within_cells", lambda *args: (same_u_lane, None))

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="Size 32: the tuples do not hold exactly 1 per lane"):
        generate_mc_tuples(t_total_sec=1.0)
