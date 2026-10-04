"""`generate_mc_tuples` builds a nested set with exactly 1 tuple per lane at every size and reports each step, and its
`MCTuplesGenerator` splits the total time over the solves and scales down the worker count of a short run."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import (
    MCTuplesCellSelectionResult,
    MCTuplesGenerator,
    MCTuplesRefinementResult,
    MCTuplesSize,
    MCTuplesStats,
    MCTuplesStepKind,
    MCTuplesStepResult,
    generate_mc_tuples,
)
from sunnbear._core.benchmark.mc_tuples.construction_steps import MCTuplesStep
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_nested_sizes_with_1_tuple_per_lane_and_reports_each_step():
    """A 1 s construction up to size 64 builds sizes 32 and 64, each with 1 tuple per lane, and reports its 4 steps in
    order, each with its selected cells or the size's tuples.

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
    assert results[-1].tuples.tuple_array.tolist() == tuples.tuple_array.tolist()
    assert results[-1].tuple_array.tolist() == tuples.tuple_array.tolist()
    assert all(MCTuplesStats(result.tuple_array).size == int(result.size) for result in results)
    assert all(result.solution.score_checkpoints for result in results)


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
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        generate_mc_tuples(t_total_sec, n_workers=n_workers, max_size=max_size)


# ==================================================================================================
#  MCTuplesGenerator: workers and time per solve
# ==================================================================================================
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


def test_every_step_kind_has_a_fixed_share_and_the_shares_sum_to_1():
    """`T_BUDGET_FRACTION_PER_STEP_KIND` names every step class once, and the shares add up to the whole total."""
    # --- act / assert -----------------
    assert set(MCTuplesGenerator.T_BUDGET_FRACTION_PER_STEP_KIND) == set(MCTuplesStep.__subclasses__())
    assert sum(MCTuplesGenerator.T_BUDGET_FRACTION_PER_STEP_KIND.values()) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "t_total_sec, max_size",
    [(1.0, MCTuplesSize.SIZE_64), (30.0, MCTuplesSize.SIZE_256), (28_800.0, MCTuplesSize.SIZE_1024)],
)
def test_t_budget_per_solve_sec_splits_each_step_s_share_by_1_percent_per_solve_and_the_rest_by_work(
    t_total_sec, max_size
):
    """Within a step kind's share, each size's solve gets 1 % of the total; the rest goes by candidates times size."""
    # --- act --------------------------
    budgets = MCTuplesGenerator().t_budget_per_solve_sec(t_total_sec, max_size)

    # --- assert -----------------------
    sizes = MCTuplesSize.up_to(max_size)
    shares = MCTuplesGenerator.T_BUDGET_FRACTION_PER_STEP_KIND
    assert set(budgets) == {(size, step_cls) for size in sizes for step_cls in shares}
    for step_cls, t_budget_fraction in shares.items():
        step_budgets = {
            size: t_budget_sec
            for (size, budget_step_cls), t_budget_sec in budgets.items()
            if budget_step_cls is step_cls
        }
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
