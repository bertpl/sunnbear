"""`MCTuplesPopulation.draw` spreads its candidates evenly over the fine lanes and fine cells that it is allowed, and,
given `MCTuplesAxisGapAllocation.eligible_fine_lanes`, draws its candidates only in the eligible fine lanes."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, fine_lanes_of
from sunnbear._core.benchmark.mc_tuples.construction.allocation import MCTuplesGapAllocation
from sunnbear._core.benchmark.mc_tuples.construction.population import MCTuplesPopulation

# The allowed fine lanes: every 16th fine lane along u, and 128 consecutive fine lanes along v: 64 x 128 fine cells.
_ALLOWED_U_LANES = np.arange(0, N_FINE_LANES, 16)
_ALLOWED_V_LANES = np.arange(512, 640)


@pytest.mark.parametrize(
    "n_population",
    [
        50,  # fewer than the allowed fine lanes
        5000,  # fewer than the allowed fine cells: at most 1 per cell
        64 * 128,  # exactly 1 per allowed fine cell
        3 * 64 * 128 + 77,  # 3 or 4 per allowed fine cell
    ],
)
def test_draw_spreads_the_candidates_evenly_over_the_allowed_fine_lanes_and_cells(n_population):
    """Every allowed fine lane, and every allowed fine cell, holds the same number of candidates, give or take 1; no
    other holds any; and each candidate lies inside its fine cell, in the open unit square."""
    # --- act --------------------------
    population = MCTuplesPopulation.draw(n_population, _ALLOWED_U_LANES, _ALLOWED_V_LANES, np.random.default_rng(1))

    # --- assert -----------------------
    assert population.u.size == population.tuple_array.shape[0] == n_population
    for lanes, allowed in ((population.u_lane, _ALLOWED_U_LANES), (population.v_lane, _ALLOWED_V_LANES)):
        counts = np.bincount(lanes, minlength=N_FINE_LANES)
        assert counts[allowed].max() - counts[allowed].min() <= 1
        assert counts[allowed].sum() == n_population
    cells = np.bincount(population.u_lane * N_FINE_LANES + population.v_lane, minlength=N_FINE_LANES**2)
    allowed_cells = cells.reshape(N_FINE_LANES, N_FINE_LANES)[np.ix_(_ALLOWED_U_LANES, _ALLOWED_V_LANES)]
    assert allowed_cells.max() - allowed_cells.min() <= 1
    assert allowed_cells.sum() == n_population
    for values, lanes in ((population.u, population.u_lane), (population.v, population.v_lane)):
        assert np.array_equal(fine_lanes_of(values), lanes)
        assert np.all((values > 0) & (values < 1))


def test_draw_over_eligible_fine_lanes_skips_the_free_fine_lanes_of_gaps_without_new_tuples():
    """The size below holds tuples in fine lanes 3, 10 and 11 on both axes, and the allocation puts both of its 2 new
    tuples in the widest gap, the one above lane 11, so the population covers exactly the fine lanes from 12 up."""
    # --- arrange ----------------------
    values = np.array([3.5, 10.25, 11.5]) / N_FINE_LANES
    gap_allocation = MCTuplesGapAllocation.of(np.column_stack([values, values]), 2)

    # --- act --------------------------
    population = MCTuplesPopulation.draw(
        3000, gap_allocation.u.eligible_fine_lanes, gap_allocation.v.eligible_fine_lanes, np.random.default_rng(4)
    )

    # --- assert -----------------------
    assert population.u.size == 3000
    for lanes in (population.u_lane, population.v_lane):
        assert lanes.min() == 12
        assert np.unique(lanes).size == N_FINE_LANES - 12


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
