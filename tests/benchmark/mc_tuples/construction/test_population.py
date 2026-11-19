"""`MCTuplesPopulation` draws its 3 kinds of candidates:

- `draw_1_in_each_lhs_cell` draws 1 candidate inside each given LHS cell;
- `draw_in_off_diagonal_cells` spreads its candidates evenly over the off-diagonal LHS cells of the given lanes, inside
  the given tiles;
- `draw_in_lhs_cells_of` draws its candidates inside the LHS cells of given base tuples;

and every value of all 3, and its mirror, holds at least `MIN_N_BITS` bits. `pick_or_draw_in_lhs_cells` picks 1
candidate in each given LHS cell, and draws one where the population holds none.
"""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MIN_N_BITS, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.population import MCTuplesPopulation
from sunnbear._core.utils.float_bits import n_bits

_SIZE = MCTuplesSize.SIZE_256

# The free lower-half LHS lanes of size 256 are every 2nd lane of [0, 0.5], which gives 64 x 64 LHS cells, 64 of them
# on the diagonal.
_FREE_LANES = np.arange(0, _SIZE.n_lower_half_lhs_lanes, 2)

# Every lower-half tile of size 256 (8 x 8 tiles of 16 x 16 LHS cells each) is free.
_ALL_LOWER_HALF_TILES = _SIZE.lower_half_tile_indices


def test_draw_1_in_each_lhs_cell_draws_1_candidate_inside_each_given_cell():
    """Each candidate lies inside the LHS cell of size 64 that its pair of lanes names."""
    # --- arrange ----------------------
    u_lanes, v_lanes = np.array([0, 5, 31, 5]), np.array([31, 2, 0, 2])

    # --- act --------------------------
    population = MCTuplesPopulation.draw_1_in_each_lhs_cell(
        u_lanes, v_lanes, MCTuplesSize.SIZE_64, np.random.default_rng(4)
    )

    # --- assert -----------------------
    assert MCTuplesSize.SIZE_64.lhs_lane_indices(population.u).tolist() == u_lanes.tolist()
    assert MCTuplesSize.SIZE_64.lhs_lane_indices(population.v).tolist() == v_lanes.tolist()
    assert population.u[1] != population.u[3]  # 2 candidates in 1 cell lie at different positions


@pytest.mark.parametrize(
    "n_population",
    [
        50,  # fewer than the free lanes
        64 * 64,  # exactly 1 per LHS cell, before the diagonal cells are dropped
        3 * 64 * 64 + 77,  # 3 or 4 per LHS cell
    ],
)
def test_draw_in_off_diagonal_cells_spreads_the_candidates_evenly_over_the_off_diagonal_cells_of_the_free_lanes(
    n_population,
):
    """With every lower-half tile free, every off-diagonal LHS cell of the free lanes holds the same number of
    candidates, give or take 1; no diagonal cell and no other lane holds any; and each candidate lies in the open
    interval (0, 0.5)."""
    # --- act --------------------------
    population = MCTuplesPopulation.draw_in_off_diagonal_cells(
        n_population, _FREE_LANES, _ALL_LOWER_HALF_TILES, _SIZE, np.random.default_rng(1)
    )

    # --- assert -----------------------
    assert population.base_tuple_array.shape == (population.u.size, 2)
    u_lanes, v_lanes = _SIZE.lhs_lane_indices(population.u), _SIZE.lhs_lane_indices(population.v)
    assert not np.any(u_lanes == v_lanes)
    cells = np.zeros((int(_SIZE), int(_SIZE)), dtype=np.int64)
    np.add.at(cells, (u_lanes, v_lanes), 1)
    free_cells = cells[np.ix_(_FREE_LANES, _FREE_LANES)]
    off_diagonal_cells = free_cells[~np.eye(_FREE_LANES.size, dtype=bool)]
    assert off_diagonal_cells.max() - off_diagonal_cells.min() <= 1
    assert off_diagonal_cells.sum() == cells.sum() == population.u.size
    for values in (population.u, population.v):
        assert np.all((values > 0) & (values < 0.5))


def test_draw_in_off_diagonal_cells_keeps_only_the_candidates_in_the_free_tiles():
    """With only 2 of the 64 lower-half tiles free, every candidate lies in 1 of them, and both hold candidates."""
    # --- arrange ----------------------
    free_tiles = np.array([0, 16 * 7 + 3])

    # --- act --------------------------
    population = MCTuplesPopulation.draw_in_off_diagonal_cells(
        64 * 64 * 8, _FREE_LANES, free_tiles, _SIZE, np.random.default_rng(1)
    )

    # --- assert -----------------------
    assert np.unique(_SIZE.tile_indices(population.u, population.v)).tolist() == free_tiles.tolist()


def test_draw_in_lhs_cells_of_puts_each_base_tuple_first_and_its_candidates_inside_its_lhs_cell():
    """Each of the 3 base tuples is followed by its 5 candidates, which all lie in its LHS cell of size 1024, at
    distinct positions."""
    # --- arrange ----------------------
    size = MCTuplesSize.SIZE_1024
    base_tuple_array = np.array([[3.5, 400.25], [10.75, 2.5], [511.5, 255.9]]) / 1024

    # --- act --------------------------
    population = MCTuplesPopulation.draw_in_lhs_cells_of(base_tuple_array, 5, size, np.random.default_rng(2))

    # --- assert -----------------------
    assert population.u.size == 18
    assert np.array_equal(population.base_tuple_array[::6], base_tuple_array)
    for values, column in ((population.u, 0), (population.v, 1)):
        assert np.array_equal(
            size.lhs_lane_indices(values), np.repeat(size.lhs_lane_indices(base_tuple_array[:, column]), 6)
        )
        assert np.unique(values).size == 18


def test_pick_or_draw_in_lhs_cells_picks_a_candidate_inside_each_cell_and_draws_one_where_none_lies():
    """Of 2 LHS cells of size 16, the first holds 2 of the population's 3 candidates and the second none: the first
    takes 1 of its 2, and the second a new candidate, appended to the population."""
    # --- arrange ----------------------
    size = MCTuplesSize.SIZE_16
    population = MCTuplesPopulation(u=np.array([0.11, 0.3, 0.12]), v=np.array([0.41, 0.2, 0.42]))

    # --- act --------------------------
    extended, picked = population.pick_or_draw_in_lhs_cells(
        np.array([1, 7]), np.array([6, 0]), size, np.random.default_rng(8)
    )

    # --- assert -----------------------
    assert extended.base_tuple_array[:3].tolist() == population.base_tuple_array.tolist()
    assert extended.u.size == 4
    assert picked[0] in (0, 2)
    assert picked[1] == 3
    assert size.lhs_lane_indices(extended.base_tuple_array[3]).tolist() == [7, 0]


def test_every_drawn_value_and_its_mirror_hold_at_least_min_n_bits():
    """Every value that the populations draw holds at least `MIN_N_BITS` bits, and so does its mirror 1 - value, which
    the set also holds; drawn at random, about 1 mirror in 5 holds fewer."""
    # --- arrange ----------------------
    rng = np.random.default_rng(3)
    base_tuple_array = np.array([[3.5, 400.25], [10.75, 2.5]]) / 1024

    # --- act --------------------------
    off_diagonal = MCTuplesPopulation.draw_in_off_diagonal_cells(2000, _FREE_LANES, _ALL_LOWER_HALF_TILES, _SIZE, rng)
    in_lhs_cells = MCTuplesPopulation.draw_in_lhs_cells_of(base_tuple_array, 500, MCTuplesSize.SIZE_1024, rng)

    # --- assert -----------------------
    drawn_values = np.concatenate(
        [off_diagonal.u, off_diagonal.v, np.delete(in_lhs_cells.base_tuple_array, np.s_[::501], axis=0).ravel()]
    )
    assert drawn_values.size == 2 * off_diagonal.u.size + 2000
    assert min(n_bits(float(value)) for value in drawn_values) >= MIN_N_BITS
    assert min(n_bits(1.0 - float(value)) for value in drawn_values) >= MIN_N_BITS
