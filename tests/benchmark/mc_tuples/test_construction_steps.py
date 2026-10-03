"""The construction steps count their candidates, and refuse a max-div selection that breaks their constraints."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesConstructionError, construction_steps
from sunnbear._core.benchmark.mc_tuples.construction_steps import (
    N_CANDIDATES_PER_CELL,
    MCTuplesConstructionStep,
    refine_within_cells,
    select_cells,
)
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid

# A set of 4 tuples; at size 8 it gets 4 new lanes per axis, crossing in 16 cells.
_SIZE_4 = MCTuples([0.15, 0.3, 0.7, 0.8], [0.8, 0.05, 0.45, 0.55])


def _run_max_div_returning(selection: list[int]):
    """Return a replacement for `construction_steps._run_max_div` that returns `selection` whatever the problem."""

    def solve(*args, **kwargs) -> np.ndarray:
        return np.array(selection)

    return solve


@pytest.mark.parametrize(
    "size, step, n_candidates",
    [
        (32, MCTuplesConstructionStep.CELL_SELECTION, 32 * 32),  # all cells, no size below
        (32, MCTuplesConstructionStep.REFINEMENT, N_CANDIDATES_PER_CELL * 32),
        (1024, MCTuplesConstructionStep.CELL_SELECTION, 512 * 512 + 512),  # the new cells and the size below
        (1024, MCTuplesConstructionStep.REFINEMENT, N_CANDIDATES_PER_CELL * 512 + 512),
    ],
)
def test_n_candidates_counts_the_new_candidates_and_the_size_below(size, step, n_candidates):
    """`n_candidates` counts a step's new candidates and, above the smallest size, the tuples of the size below."""
    # --- act / assert -----------------
    assert step.n_candidates(size) == n_candidates


@pytest.mark.parametrize(
    "selection, message",
    [
        ([0, 1, 2, 4, 5, 6, 7, 8], "1 tuples of the size below it are not selected"),  # tuple 3 missing
        ([0, 1, 2, 3, 4, 5, 6, 7], "do not hold exactly 1 per new lane"),  # the 4 cells of the first new u lane
    ],
)
def test_select_cells_refuses_a_missing_tuple_or_2_cells_in_1_lane(monkeypatch, selection, message):
    """A cell selection without every tuple of the size below, or with 2 cells in 1 new lane, raises an error."""
    # --- arrange ----------------------
    monkeypatch.setattr(construction_steps, "_run_max_div", _run_max_div_returning(selection))

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match=message):
        select_cells(LaneGrid.for_size(8, _SIZE_4), 1.0, 1, 42, np.random.default_rng(0))


def test_refine_within_cells_refuses_2_tuples_in_1_cell(monkeypatch):
    """A refinement that selects 2 candidates of the first cell, and none of the second, raises an error."""
    # --- arrange ----------------------
    two_in_first_cell = [0, 1, 2, 3, 4, 5, 4 + 2 * N_CANDIDATES_PER_CELL, 4 + 3 * N_CANDIDATES_PER_CELL]
    monkeypatch.setattr(construction_steps, "_run_max_div", _run_max_div_returning(two_in_first_cell))

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="1 new tuple per cell"):
        refine_within_cells(
            LaneGrid.for_size(8, _SIZE_4), np.array([2, 4, 11, 13]), 1.0, 1, 42, np.random.default_rng(0)
        )
