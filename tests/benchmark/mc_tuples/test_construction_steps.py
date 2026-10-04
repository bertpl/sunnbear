"""The construction steps count their candidates, and refuse a max-div selection that breaks their constraints."""

import numpy as np
import pytest
from max_div.metrics import DistanceMetric, DiversityMetric

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesConstructionError
from sunnbear._core.benchmark.mc_tuples.construction_steps import (
    N_CANDIDATES_PER_CELL,
    MCTuplesCellSelectionStep,
    MCTuplesRefinementStep,
    MCTuplesSolveSettings,
    MCTuplesStep,
)
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid

# A set of 4 tuples; size 8, built on it, has 4 new lanes per axis, crossing in 16 cells.
_SIZE_4 = MCTuples([0.15, 0.3, 0.7, 0.8], [0.8, 0.05, 0.45, 0.55])
_SETTINGS = MCTuplesSolveSettings.for_seed(n_workers=1, seed=42)


def _run_max_div_returning(selection: list[int]):
    """Return a replacement for `MCTuplesStep._run_max_div` that returns `selection`, and no solution."""

    def solve(self, *args, **kwargs) -> tuple[np.ndarray, None]:
        """Return `selection` and no solution, whatever the arguments."""
        return np.array(selection), None

    return solve


@pytest.mark.parametrize(
    "size, step_cls, n_candidates",
    [
        (32, MCTuplesCellSelectionStep, 32 * 32),  # all cells, no size below
        (32, MCTuplesRefinementStep, N_CANDIDATES_PER_CELL * 32),
        (1024, MCTuplesCellSelectionStep, 512 * 512 + 512),  # the new cells and the size below
        (1024, MCTuplesRefinementStep, N_CANDIDATES_PER_CELL * 512 + 512),
    ],
)
def test_n_candidates_counts_the_new_candidates_and_the_size_below(size, step_cls, n_candidates):
    """`n_candidates` counts a step's new candidates and, above the smallest size, the tuples of the size below."""
    # --- act / assert -----------------
    assert step_cls.n_candidates(size) == n_candidates


@pytest.mark.parametrize(
    "selection, message",
    [
        ([0, 1, 2, 4, 5, 6, 7, 8], "1 tuples of the size below it are not selected"),  # tuple 3 missing
        ([0, 1, 2, 3, 4, 5, 6, 7], "do not hold exactly 1 per new lane"),  # the 4 cells of the first new u lane
    ],
)
def test_cell_selection_refuses_a_missing_tuple_or_2_cells_in_1_lane(monkeypatch, selection, message):
    """A cell selection without every tuple of the size below, or with 2 cells in 1 new lane, raises an error."""
    # --- arrange ----------------------
    monkeypatch.setattr(MCTuplesStep, "_run_max_div", _run_max_div_returning(selection))
    step = MCTuplesCellSelectionStep(LaneGrid.for_size(8, _SIZE_4), _SETTINGS)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match=message):
        step.run(1.0)


@pytest.mark.parametrize(
    "cells, selection, message",
    [
        # 1 cell per new lane, but 2 candidates of the first cell selected and none of the second.
        (
            [2, 4, 11, 13],
            [0, 1, 2, 3, 4, 5, 4 + 2 * N_CANDIDATES_PER_CELL, 4 + 3 * N_CANDIDATES_PER_CELL],
            "1 new tuple per cell",
        ),
        # 1 candidate per cell, but the 4 cells share the first new u lane, so 4 tuples end up in 1 lane.
        (
            [0, 1, 2, 3],
            [0, 1, 2, 3, 4, 4 + N_CANDIDATES_PER_CELL, 4 + 2 * N_CANDIDATES_PER_CELL, 4 + 3 * N_CANDIDATES_PER_CELL],
            "exactly 1 per lane",
        ),
    ],
)
def test_refinement_refuses_2_tuples_in_1_cell_or_in_1_lane(monkeypatch, cells, selection, message):
    """A refinement with 2 tuples in 1 cell, or with the size's tuples not 1 per lane, raises an error."""
    # --- arrange ----------------------
    monkeypatch.setattr(MCTuplesStep, "_run_max_div", _run_max_div_returning(selection))
    step = MCTuplesRefinementStep(LaneGrid.for_size(8, _SIZE_4), np.array(cells), _SETTINGS)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match=message):
        step.run(1.0)


@pytest.mark.parametrize(
    "build_step, distance_metric",
    [
        (lambda grid: MCTuplesCellSelectionStep(grid, _SETTINGS), DistanceMetric.l2_euclidean()),
        (
            lambda grid: MCTuplesRefinementStep(grid, np.array([2, 4, 11, 13]), _SETTINGS),
            DistanceMetric.l2_and_projections(k=8),
        ),
    ],
)
def test_each_step_maximizes_min_separation_over_its_own_distance(monkeypatch, build_step, distance_metric):
    """Cell selection maximizes min separation over L2, refinement over `l2_and_projections` for the grid's size."""
    # --- arrange ----------------------
    objectives: list[tuple[DiversityMetric, DistanceMetric]] = []

    def record_the_objective(self, new_candidate_array, diversity_metric, distance_metric, *args):
        """Record the objective and return an empty selection, which the step then rejects."""
        objectives.append((diversity_metric, distance_metric))
        return np.array([], dtype=np.int64), None

    monkeypatch.setattr(MCTuplesStep, "_solve", record_the_objective)
    step = build_step(LaneGrid.for_size(8, _SIZE_4))

    # --- act --------------------------
    with pytest.raises(MCTuplesConstructionError):
        step.run(1.0)

    # --- assert -----------------------
    assert objectives == [(DiversityMetric.MIN_SEPARATION, distance_metric)]
