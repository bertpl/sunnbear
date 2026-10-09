"""`generate_mc_tuples` builds nested sizes with means of 0.5 and at most 1 tuple per fine lane, and reports each size;
its `MCTuplesGenerator` splits the total time over the solves and scales down the worker count of a short run."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import (
    N_FINE_LANES,
    MCTuples,
    MCTuplesGenerator,
    MCTuplesSize,
    MCTuplesSizeResult,
    fine_lanes_of,
    generate_mc_tuples,
)
from sunnbear._core.benchmark.mc_tuples.construction_solve import MCTuplesSizeSolve


def _spread_each_gap_s_new_tuples(self: MCTuplesSizeSolve, t_budget_sec: float) -> tuple[np.ndarray, None]:
    """Replace `MCTuplesSizeSolve.run`: spread each gap's new tuples evenly over its fine lanes, pair u and v at random,
    and return them without running max-div."""
    new_values = []
    for allocation in (self.gap_allocation.u, self.gap_allocation.v):
        values = []
        for gap, count in enumerate(allocation.counts):
            lanes = np.flatnonzero(allocation.gap_of_fine_lane == gap)
            picks = np.round(np.linspace(0, lanes.size - 1, count + 2)[1:-1]).astype(np.int64)
            values.extend((lanes[picks] + 0.5) / N_FINE_LANES)
        new_values.append(self.settings.rng.permutation(values))
    return np.column_stack(new_values), None


def _assert_valid_nested_set(tuples: MCTuples, results: list[MCTuplesSizeResult]) -> None:
    """Assert that every reported size is a prefix of `tuples`, with means of 0.5 and at most 1 tuple per fine lane."""
    for result in results:
        size_tuples = tuples.first(result.size)
        assert result.tuples.tuple_array.tolist() == size_tuples.tuple_array.tolist()
        assert size_tuples.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5], abs=1e-12)
        for values in (size_tuples.u, size_tuples.v):
            assert np.bincount(fine_lanes_of(values)).max() == 1


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_nested_sizes_with_means_of_0_5_and_reports_each_size():
    """A 2 s construction up to size 64 builds sizes 32 and 64, each with means of 0.5 and at most 1 tuple per fine
    lane, and reports both sizes in order.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- arrange ----------------------
    results: list[MCTuplesSizeResult] = []

    # --- act --------------------------
    tuples = generate_mc_tuples(
        t_total_sec=2.0, max_size=MCTuplesSize.SIZE_64, n_population=2**14, on_size_finished=results.append
    )

    # --- assert -----------------------
    assert tuples.size == 64
    assert [int(result.size) for result in results] == [32, 64]
    _assert_valid_nested_set(tuples, results)
    assert all(result.uncorrected_tuple_array.shape == (int(result.size), 2) for result in results)
    assert all(result.solution.score_checkpoints for result in results)


def test_generate_mc_tuples_corrects_each_size_and_builds_the_next_on_it(monkeypatch):
    """With the solve replaced by a stub that spreads each gap's new tuples evenly over its fine lanes, the generator
    corrects every size's means to 0.5 and builds each size on the corrected size below."""
    # --- arrange ----------------------
    monkeypatch.setattr(MCTuplesSizeSolve, "run", _spread_each_gap_s_new_tuples)
    results: list[MCTuplesSizeResult] = []

    # --- act --------------------------
    tuples = generate_mc_tuples(
        t_total_sec=1.0, max_size=MCTuplesSize.SIZE_128, n_population=2**12, on_size_finished=results.append
    )

    # --- assert -----------------------
    assert tuples.size == 128
    assert [int(result.size) for result in results] == [32, 64, 128]
    _assert_valid_nested_set(tuples, results)
    assert results[0].gap_allocation.u.mean_aware_offset_fine_lanes is None
    assert results[1].gap_allocation.u.mean_aware_offset_fine_lanes is not None


def test_generate_mc_tuples_without_a_callback_returns_the_largest_size(monkeypatch):
    """Without `on_size_finished`, the generator reports nothing and returns the largest size, corrected to 0.5."""
    # --- arrange ----------------------
    monkeypatch.setattr(MCTuplesSizeSolve, "run", _spread_each_gap_s_new_tuples)

    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0, max_size=MCTuplesSize.SIZE_64, n_population=2**12)

    # --- assert -----------------------
    assert tuples.size == 64
    assert tuples.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5], abs=1e-12)


@pytest.mark.parametrize(
    "arguments, message",
    [
        ({"t_total_sec": 0.5}, "at least 1.0 s"),
        ({"t_total_sec": 60.0, "n_workers": 0}, "n_workers must be at least 1"),
        ({"t_total_sec": 60.0, "max_size": 100}, "must be one of"),
        ({"t_total_sec": 60.0, "n_population": 0}, "n_population must be at least 1"),
        ({"t_total_sec": 60.0, "allocation_epsilon": 1.0}, r"allocation_epsilon must lie in \[0, 1\)"),
        ({"t_total_sec": 60.0, "allocation_epsilon": -0.1}, r"allocation_epsilon must lie in \[0, 1\)"),
    ],
)
def test_generate_mc_tuples_rejects_invalid_arguments(arguments, message):
    """A total below 1 s, no workers, an unknown size, an empty population or an ε outside [0, 1) raise a
    `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        generate_mc_tuples(**arguments)


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


@pytest.mark.parametrize(
    "t_total_sec, max_size, n_population",
    [
        (1.0, MCTuplesSize.SIZE_64, 2**14),
        (30.0, MCTuplesSize.SIZE_256, 2**18),
        (28_800.0, MCTuplesSize.SIZE_1024, 2**20),
    ],
)
def test_t_budget_per_solve_sec_gives_each_solve_1_percent_and_splits_the_rest_by_work(
    t_total_sec, max_size, n_population
):
    """Each size's solve gets 1 % of the total, plus a part of the rest in proportion to its size times its number of
    candidates, which is the population plus the tuples of the size below."""
    # --- act --------------------------
    budgets = MCTuplesGenerator(n_population=n_population).t_budget_per_solve_sec(t_total_sec, max_size)

    # --- assert -----------------------
    sizes = MCTuplesSize.up_to(max_size)
    work_per_size = {size: (n_population + size.n_required) * size for size in sizes}
    t_rest_sec = t_total_sec - 0.01 * t_total_sec * len(sizes)
    assert budgets == pytest.approx(
        {
            size: 0.01 * t_total_sec + t_rest_sec * work / sum(work_per_size.values())
            for size, work in work_per_size.items()
        }
    )
    assert sum(budgets.values()) == pytest.approx(t_total_sec)
