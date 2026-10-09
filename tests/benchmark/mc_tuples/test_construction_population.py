"""`MCTuplesPopulation.draw` spreads its candidates evenly over the free fine lanes and the free fine cells."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, fine_lanes_of
from sunnbear._core.benchmark.mc_tuples.construction_population import MCTuplesPopulation

# Every 16th fine lane is free along u, and 128 consecutive fine lanes along v: 64 x 128 free fine cells.
_FREE_U_LANES = np.arange(0, N_FINE_LANES, 16)
_FREE_V_LANES = np.arange(512, 640)


@pytest.mark.parametrize(
    "n_candidates",
    [
        50,  # fewer than the free fine lanes
        5000,  # fewer than the free fine cells: at most 1 per cell
        64 * 128,  # exactly 1 per free fine cell
        3 * 64 * 128 + 77,  # 3 or 4 per free fine cell
    ],
)
def test_draw_spreads_the_candidates_evenly_over_the_free_fine_lanes_and_cells(n_candidates):
    """Every free fine lane, and every free fine cell, holds the same number of candidates, give or take 1; no other
    holds any; and each candidate lies inside its fine cell, in the open unit square."""
    # --- act --------------------------
    population = MCTuplesPopulation.draw(n_candidates, _FREE_U_LANES, _FREE_V_LANES, np.random.default_rng(1))

    # --- assert -----------------------
    assert population.u.size == population.tuple_array.shape[0] == n_candidates
    for lanes, free in ((population.u_lane, _FREE_U_LANES), (population.v_lane, _FREE_V_LANES)):
        counts = np.bincount(lanes, minlength=N_FINE_LANES)
        assert counts[free].max() - counts[free].min() <= 1
        assert counts[free].sum() == n_candidates
    cells = np.bincount(population.u_lane * N_FINE_LANES + population.v_lane, minlength=N_FINE_LANES**2)
    free_cells = cells.reshape(N_FINE_LANES, N_FINE_LANES)[np.ix_(_FREE_U_LANES, _FREE_V_LANES)]
    assert free_cells.max() - free_cells.min() <= 1
    assert free_cells.sum() == n_candidates
    for values, lanes in ((population.u, population.u_lane), (population.v, population.v_lane)):
        assert np.array_equal(fine_lanes_of(values), lanes)
        assert np.all((values > 0) & (values < 1))


def test_draw_rejects_an_empty_population():
    """A population of fewer than 1 candidate raises a `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="must be positive"):
        MCTuplesPopulation.draw(0, _FREE_U_LANES, _FREE_V_LANES, np.random.default_rng(1))


def test_randomize_pattern_keeps_every_row_and_column_count():
    """Curveball trades change which cells are occupied, but no row's or column's count."""
    # --- arrange ----------------------
    rng = np.random.default_rng(2)
    is_occupied = MCTuplesPopulation._round_robin_pattern(20, 30, 250, rng)
    before = is_occupied.copy()

    # --- act --------------------------
    MCTuplesPopulation._randomize_pattern(is_occupied, 500, rng)

    # --- assert -----------------------
    assert not np.array_equal(is_occupied, before)
    assert np.array_equal(is_occupied.sum(axis=0), before.sum(axis=0))
    assert np.array_equal(is_occupied.sum(axis=1), before.sum(axis=1))


def test_positions_in_lane_move_a_draw_of_exactly_0_to_the_middle_of_its_lane():
    """A position of exactly 0 would put a candidate on the edge of the unit square; it becomes 0.5."""

    # --- arrange ----------------------
    class _ZerosFirst:
        """`_ZerosFirst` stands in for a random generator whose `random` draws 0 first."""

        def random(self, n: int) -> np.ndarray:
            """Return 0 followed by 0.25's."""
            return np.concatenate([[0.0], np.full(n - 1, 0.25)])

    # --- act --------------------------
    positions = MCTuplesPopulation._positions_in_lane(3, _ZerosFirst())  # type: ignore[arg-type]

    # --- assert -----------------------
    assert positions.tolist() == [0.5, 0.25, 0.25]
