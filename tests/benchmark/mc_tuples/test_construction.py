"""`generate_mc_tuples` builds a nested set with exactly 1 tuple per lane at every size and reports each step, and its
`MCTuplesGenerator` splits the total time over the solves and scales the workers of a short run down."""

from typing import TYPE_CHECKING, cast

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import (
    MCTuples,
    MCTuplesCellSelectionResult,
    MCTuplesConstructionError,
    MCTuplesGenerator,
    MCTuplesRefinementResult,
    MCTuplesSize,
    MCTuplesStepKind,
    MCTuplesStepResult,
    generate_mc_tuples,
)
from sunnbear._core.benchmark.mc_tuples.construction_steps import (
    MCTuplesCellSelectionStep,
    MCTuplesConstructionStep,
    MCTuplesRefinementStep,
)
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid

if TYPE_CHECKING:
    from max_div.solver import ParallelMaxDivSolution


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_nested_sizes_with_1_tuple_per_lane_and_reports_each_step():
    """A 1 s construction up to size 64 builds sizes 32 and 64, each with 1 tuple per lane, and reports its 4 steps in
    order, each with the step's own product.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- arrange ----------------------
    results: list[MCTuplesStepResult] = []

    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0, max_size=MCTuplesSize.SIZE_64, on_solve_finished=results.append)

    # --- assert -----------------------
    assert tuples.size == 64
    assert LaneGrid.is_one_per_lane_on_rebuilt_grid(tuples.first(32))
    assert LaneGrid.is_one_per_lane_on_rebuilt_grid(tuples)
    assert np.unique(tuples.u).size == np.unique(tuples.v).size == 64
    assert [(int(result.size), result.kind) for result in results] == [
        (32, MCTuplesStepKind.CELL_SELECTION),
        (32, MCTuplesStepKind.REFINEMENT),
        (64, MCTuplesStepKind.CELL_SELECTION),
        (64, MCTuplesStepKind.REFINEMENT),
    ]
    assert isinstance(results[0], MCTuplesCellSelectionResult)
    assert results[0].tuple_array.shape == (32, 2)
    assert results[0].cells.shape == (32,)
    assert isinstance(results[-1], MCTuplesRefinementResult)
    assert results[-1].new_tuples.size == 32
    assert results[-1].tuple_array.tolist() == tuples.tuple_array.tolist()
    assert all(result.stats().size == int(result.size) for result in results)
    assert all(result.solution.score_checkpoints for result in results)


def test_generate_mc_tuples_refuses_a_size_without_1_tuple_per_lane(monkeypatch):
    """A size whose tuples share a lane raises an error before the next size is built; the steps never produce one."""
    # --- arrange ----------------------
    no_solution = cast("ParallelMaxDivSolution", None)

    def select_the_first_row_of_cells(
        self: MCTuplesCellSelectionStep, t_budget_sec: float
    ) -> MCTuplesCellSelectionResult:
        cells = np.arange(self.grid.size)
        return MCTuplesCellSelectionResult(
            size=MCTuplesSize(self.grid.size),
            kind=self.kind,
            t_budget_sec=t_budget_sec,
            t_wall_sec=0.0,
            tuple_array=self.grid.required_and_cell_tuple_array(cells),
            solution=no_solution,
            cells=cells,
        )

    def place_every_tuple_in_1_u_lane(self: MCTuplesRefinementStep, t_budget_sec: float) -> MCTuplesRefinementResult:
        same_u_lane = MCTuples(np.full(32, 0.01), (np.arange(32) + 0.5) / 32)
        return MCTuplesRefinementResult(
            size=MCTuplesSize(self.grid.size),
            kind=self.kind,
            t_budget_sec=t_budget_sec,
            t_wall_sec=0.0,
            tuple_array=same_u_lane.tuple_array,
            solution=no_solution,
            new_tuples=same_u_lane,
        )

    monkeypatch.setattr(MCTuplesCellSelectionStep, "run", select_the_first_row_of_cells)
    monkeypatch.setattr(MCTuplesRefinementStep, "run", place_every_tuple_in_1_u_lane)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="Size 32: the tuples do not hold exactly 1 per lane"):
        generate_mc_tuples(t_total_sec=1.0, max_size=MCTuplesSize.SIZE_64)


@pytest.mark.parametrize(
    "t_total_sec, n_workers, max_size, message",
    [
        (0.5, 32, MCTuplesSize.SIZE_1024, "at least 1.0 s"),
        (60.0, 0, MCTuplesSize.SIZE_1024, "n_workers must be at least 1"),
        (60.0, 32, 100, "must be one of"),
    ],
)
def test_generate_mc_tuples_rejects_a_total_below_1_s_no_workers_or_an_unknown_size(
    t_total_sec, n_workers, max_size, message
):
    """A total below 1 s, fewer than 1 worker, or a `max_size` outside `MCTuplesSize` raises a `ValueError`."""
    with pytest.raises(ValueError, match=message):
        generate_mc_tuples(t_total_sec, n_workers=n_workers, max_size=max_size)


# ==================================================================================================
#  MCTuplesGenerator: sizes, workers and time per solve
# ==================================================================================================
@pytest.mark.parametrize(
    "max_size, sizes",
    [
        (MCTuplesSize.SIZE_32, (32,)),
        (MCTuplesSize.SIZE_64, (32, 64)),
        (MCTuplesSize.SIZE_1024, tuple(MCTuplesSize)),
    ],
)
def test_sizes_up_to_lists_every_size_up_to_max_size(max_size, sizes):
    """The sizes of a construction are every size of `MCTuplesSize` up to `max_size`, the smallest first."""
    # --- act / assert -----------------
    assert MCTuplesGenerator.sizes_up_to(max_size) == sizes


@pytest.mark.parametrize(
    "t_total_sec, n_workers",
    [
        (1.0, 1),  # 1 worker at the shortest run
        (15.0, 8),  # a quarter of full scale
        (30.0, 16),  # half scale
        (60.0, 32),  # full scale reached
        (28_800.0, 32),  # full scale
    ],
)
def test_n_workers_for_scales_the_workers_down_below_60_s(t_total_sec, n_workers):
    """Below 60 s, the worker count scales down with the total time, to 1 worker at 1 s; from 60 s up, all are used."""
    # --- act / assert -----------------
    assert MCTuplesGenerator(n_workers=32).n_workers_for(t_total_sec) == n_workers


def test_every_step_has_a_fixed_share_and_the_shares_sum_to_1():
    """`T_BUDGET_FRACTION_PER_STEP` names every step class once, and the shares add up to the whole total."""
    # --- act / assert -----------------
    assert set(MCTuplesGenerator.T_BUDGET_FRACTION_PER_STEP) == set(MCTuplesConstructionStep.__subclasses__())
    assert sum(MCTuplesGenerator.T_BUDGET_FRACTION_PER_STEP.values()) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "t_total_sec, max_size",
    [(1.0, MCTuplesSize.SIZE_64), (30.0, MCTuplesSize.SIZE_256), (28_800.0, MCTuplesSize.SIZE_1024)],
)
def test_t_budget_per_solve_sec_splits_each_step_s_share_by_1_percent_per_solve_and_the_rest_by_work(
    t_total_sec, max_size
):
    """Within a step's share, each solve gets 1 % of the total, and the rest is split by work.

    A solve's work is its number of candidates times its size.
    """
    # --- act --------------------------
    budgets = MCTuplesGenerator().t_budget_per_solve_sec(t_total_sec, max_size)

    # --- assert -----------------------
    sizes = MCTuplesGenerator.sizes_up_to(max_size)
    assert set(budgets) == {
        (size, step_cls) for size in sizes for step_cls in MCTuplesGenerator.T_BUDGET_FRACTION_PER_STEP
    }
    for step_cls, t_budget_fraction in MCTuplesGenerator.T_BUDGET_FRACTION_PER_STEP.items():
        step_budgets = {size: t for (size, s), t in budgets.items() if s is step_cls}
        work_per_size = {size: step_cls.n_candidates(size) * size for size in step_budgets}
        t_rest_sec = t_budget_fraction * t_total_sec - 0.01 * t_total_sec * len(step_budgets)
        assert step_budgets == pytest.approx(
            {
                size: 0.01 * t_total_sec + t_rest_sec * work / sum(work_per_size.values())
                for size, work in work_per_size.items()
            }
        )
        assert sum(step_budgets.values()) == pytest.approx(t_budget_fraction * t_total_sec)
    assert sum(budgets.values()) == pytest.approx(t_total_sec)
