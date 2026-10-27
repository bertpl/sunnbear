"""`MCTuplesGenerator`, which `generate_mc_tuples` runs:

- builds nested sizes with means of 0.5 and at most 1 tuple per fine lane;
- rotates each axis in the first value correction of the smallest size, and applies the mean correction in every other
  value correction;
- reports each size;
- splits the total time over the sizes, and each size's time over its 2 solves;
- scales down the worker count of a short run.
"""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import (
    MIN_N_BITS,
    N_FINE_LANES,
    MCTuples,
    MCTuplesGenerator,
    MCTuplesSize,
    MCTuplesSizeResult,
    fine_lanes_of,
    generate_mc_tuples,
)
from sunnbear._core.benchmark.mc_tuples.construction.refinement import MCTuplesRefinementSolve
from sunnbear._core.benchmark.mc_tuples.construction.selection import MCTuplesSelectionSolve


def _spread_each_gap_s_new_tuples(self: MCTuplesSelectionSolve, t_budget_sec: float) -> tuple[np.ndarray, None]:
    """Replace `MCTuplesSelectionSolve.run`: spread each gap's new tuples evenly over its fine lanes, pair u and v at
    random, and return them without running max-div."""
    new_values = []
    for allocation in (self.gap_allocation.u, self.gap_allocation.v):
        values = []
        for gap, count in enumerate(allocation.counts):
            lanes = np.flatnonzero(allocation.gap_of_fine_lane == gap)
            picks = np.round(np.linspace(0, lanes.size - 1, count + 2)[1:-1]).astype(np.int64)
            values.extend((lanes[picks] + 0.5) / N_FINE_LANES)
        new_values.append(self.settings.rng.permutation(values))
    return np.vstack([self.required_tuple_array, np.column_stack(new_values)]), None


def _pick_each_cell_s_last_candidate(self: MCTuplesRefinementSolve, t_budget_sec: float) -> tuple[np.ndarray, None]:
    """Replace `MCTuplesRefinementSolve.run`: pick the last candidate of each fine cell, without running max-div."""
    n_per_cell = self.n_random_candidates_per_cell + 1
    return np.vstack([self.required_tuple_array, self.population.tuple_array[n_per_cell - 1 :: n_per_cell]]), None


def _assert_valid_nested_set(tuples: MCTuples, results: list[MCTuplesSizeResult]) -> None:
    """Assert that every reported size is a prefix of `tuples`, and that in each size:

    - the u and v means are 0.5;
    - each fine lane holds at most 1 tuple;
    - every value holds at least `MIN_N_BITS` bits of information.
    """
    for result in results:
        size_tuples = tuples.first(result.size)
        assert result.tuples.tuple_array.tolist() == size_tuples.tuple_array.tolist()
        assert size_tuples.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5], abs=1e-12)
        for values in (size_tuples.u, size_tuples.v):
            assert np.bincount(fine_lanes_of(values)).max() == 1
        bit_stats = size_tuples.bit_stats()
        assert min(bit_stats.min_n_bits_u, bit_stats.min_n_bits_v) >= MIN_N_BITS


def _assert_only_the_smallest_size_s_first_correction_rotates(results: list[MCTuplesSizeResult]) -> None:
    """Assert that the first value correction of the smallest size rotates both axes, each with a `rotation_shift`,
    and that every other value correction applies the mean correction to both axes, each with a `cap`."""
    for result in results:
        is_smallest_size = result.size.size_below is None
        for correction, is_rotation in (
            (result.first_value_correction, is_smallest_size),
            (result.second_value_correction, False),
        ):
            for axis_correction in (correction.u, correction.v):
                assert (axis_correction.rotation_shift is not None) == is_rotation
                assert (axis_correction.cap is None) == is_rotation


# ==================================================================================================
#  MCTuplesGenerator and generate_mc_tuples
# ==================================================================================================
@pytest.mark.only_with_numba_jit
def test_generator_builds_nested_sizes_with_means_of_0_5_and_reports_each_size():
    """A construction up to size 64 builds sizes 32 and 64 as a valid nested set (`_assert_valid_nested_set`), rotates
    the axes only in size 32's first value correction, and reports both sizes in order.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- arrange ----------------------
    results: list[MCTuplesSizeResult] = []

    # --- act --------------------------
    generator = MCTuplesGenerator(n_population=2**14, on_size_finished=results.append)
    # Each solve's share of `t_total_sec` also covers the start of max-div's worker processes, each of which imports
    # max-div again; the worker processes start more slowly on a machine that runs other tests beside this one.
    tuples = generator.generate(t_total_sec=10.0, max_size=MCTuplesSize.SIZE_64)

    # --- assert -----------------------
    assert tuples.size == 64
    assert [int(result.size) for result in results] == [32, 64]
    _assert_valid_nested_set(tuples, results)
    _assert_only_the_smallest_size_s_first_correction_rotates(results)
    assert all(result.refined_tuple_array.shape == (int(result.size), 2) for result in results)
    assert all(result.selection_solution.score_checkpoints for result in results)
    assert all(result.refinement_solution.score_checkpoints for result in results)


def test_generator_corrects_refines_and_corrects_each_size_and_builds_the_next_on_it(monkeypatch):
    """With both solves replaced by stubs that run no max-div, the generator, for each size:

    - corrects the size's means to 0.5, rotating each axis in the smallest size's first correction only;
    - moves every corrected new tuple within its fine cell;
    - corrects the means to 0.5 again;
    - builds the next size on this corrected size.
    """
    # --- arrange ----------------------
    monkeypatch.setattr(MCTuplesSelectionSolve, "run", _spread_each_gap_s_new_tuples)
    monkeypatch.setattr(MCTuplesRefinementSolve, "run", _pick_each_cell_s_last_candidate)
    results: list[MCTuplesSizeResult] = []

    # --- act --------------------------
    generator = MCTuplesGenerator(n_population=2**12, on_size_finished=results.append)
    tuples = generator.generate(t_total_sec=1.0, max_size=MCTuplesSize.SIZE_128)

    # --- assert -----------------------
    assert tuples.size == 128
    assert [int(result.size) for result in results] == [32, 64, 128]
    _assert_valid_nested_set(tuples, results)
    _assert_only_the_smallest_size_s_first_correction_rotates(results)
    assert results[0].gap_allocation.u.mean_aware_offset_fine_lanes is None
    assert results[1].gap_allocation.u.mean_aware_offset_fine_lanes is not None
    for result in results:
        first_corrected, refined = result.first_value_correction.tuple_array, result.refined_tuple_array
        assert first_corrected.mean(axis=0) == pytest.approx([0.5, 0.5], abs=1e-12)
        assert np.array_equal(first_corrected[: result.size.n_required], refined[: result.size.n_required])
        assert not np.any(first_corrected[result.size.n_required :] == refined[result.size.n_required :])
        assert np.array_equal(fine_lanes_of(first_corrected), fine_lanes_of(refined))


def test_generate_mc_tuples_returns_the_largest_size_corrected_to_0_5(monkeypatch):
    """`generate_mc_tuples` returns the largest size, with means of 0.5."""
    # --- arrange ----------------------
    monkeypatch.setattr(MCTuplesSelectionSolve, "run", _spread_each_gap_s_new_tuples)
    monkeypatch.setattr(MCTuplesRefinementSolve, "run", _pick_each_cell_s_last_candidate)

    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0, max_size=MCTuplesSize.SIZE_64, n_population=2**12)

    # --- assert -----------------------
    assert tuples.size == 64
    assert tuples.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5], abs=1e-12)


def test_generator_splits_each_size_s_budget_8_to_1_between_selection_and_refinement(monkeypatch):
    """The selection solve of each size gets 8/9 of the size's budget, and the refinement solve the other 1/9."""
    # --- arrange ----------------------
    budgets: list[tuple[str, float]] = []

    def _record_selection_budget(self: MCTuplesSelectionSolve, t_budget_sec: float) -> tuple[np.ndarray, None]:
        """Record the selection's budget, then run the selection stub."""
        budgets.append(("selection", t_budget_sec))
        return _spread_each_gap_s_new_tuples(self, t_budget_sec)

    def _record_refinement_budget(self: MCTuplesRefinementSolve, t_budget_sec: float) -> tuple[np.ndarray, None]:
        """Record the refinement's budget, then run the refinement stub."""
        budgets.append(("refinement", t_budget_sec))
        return _pick_each_cell_s_last_candidate(self, t_budget_sec)

    monkeypatch.setattr(MCTuplesSelectionSolve, "run", _record_selection_budget)
    monkeypatch.setattr(MCTuplesRefinementSolve, "run", _record_refinement_budget)
    results: list[MCTuplesSizeResult] = []

    # --- act --------------------------
    generator = MCTuplesGenerator(n_population=2**12, on_size_finished=results.append)
    generator.generate(t_total_sec=9.0, max_size=MCTuplesSize.SIZE_64)

    # --- assert -----------------------
    assert [solve for solve, _ in budgets] == ["selection", "refinement"] * 2
    for i, result in enumerate(results):
        assert budgets[2 * i][1] == pytest.approx(8 / 9 * result.t_budget_sec)
        assert budgets[2 * i + 1][1] == pytest.approx(1 / 9 * result.t_budget_sec)


@pytest.mark.parametrize(
    "arguments, message",
    [
        ({"t_total_sec": 0.5}, "at least 1.0 s"),
        ({"t_total_sec": 60.0, "n_workers": 0}, "n_workers must be at least 1"),
        ({"t_total_sec": 60.0, "max_size": 100}, "must be one of"),
        ({"t_total_sec": 60.0, "n_population": 0}, "n_population must be at least 1"),
        (
            {"t_total_sec": 60.0, "n_refinement_random_candidates_per_cell": 0},
            "n_refinement_random_candidates_per_cell must be",
        ),
    ],
)
def test_generate_mc_tuples_rejects_invalid_arguments(arguments, message):
    """A total below 1 s, no workers, an unknown size, an empty population or no refinement candidates raise a
    `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        generate_mc_tuples(**arguments)


# ==================================================================================================
#  MCTuplesGenerator: workers and time per size
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
def test_t_budget_per_size_sec_gives_each_size_1_percent_and_splits_the_rest_by_work(
    t_total_sec, max_size, n_population
):
    """Each size gets 1 % of the total, plus a part of the rest in proportion to its size times the selection solve's
    number of candidates, which is the population plus the tuples of the size below."""
    # --- act --------------------------
    budgets = MCTuplesGenerator(n_population=n_population).t_budget_per_size_sec(t_total_sec, max_size)

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
