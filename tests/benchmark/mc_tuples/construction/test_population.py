"""`MCTuplesPopulation` draws its 2 kinds of population:

- `draw_in_off_diagonal_cells` spreads its candidates evenly over the off-diagonal fine cells of the given lanes;
- `draw_in_fine_cells_of` draws its candidates inside the fine cells of given base tuples;

and every value of both, and its mirror, holds at least `MIN_N_BITS` bits.
"""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MIN_N_BITS, N_FINE_LANES, fine_lanes_of
from sunnbear._core.benchmark.mc_tuples.construction.population import MCTuplesPopulation
from sunnbear._core.utils.float_bits import n_bits

# The free lower fine lanes are every 8th lane of [0, 0.5], which gives 64 x 64 fine cells, 64 of them on the diagonal.
_FREE_LANES = np.arange(0, N_FINE_LANES // 2, 8)


@pytest.mark.parametrize(
    "n_population",
    [
        50,  # fewer than the free lanes
        64 * 64,  # exactly 1 per fine cell, before the diagonal cells are dropped
        3 * 64 * 64 + 77,  # 3 or 4 per fine cell
    ],
)
def test_draw_in_off_diagonal_cells_spreads_the_candidates_evenly_over_the_off_diagonal_cells_of_the_free_lanes(
    n_population,
):
    """Every off-diagonal fine cell of the free lanes holds the same number of candidates, give or take 1; no diagonal
    cell and no other lane holds any; and each candidate lies inside its fine cell, in the open interval (0, 0.5)."""
    # --- act --------------------------
    population = MCTuplesPopulation.draw_in_off_diagonal_cells(n_population, _FREE_LANES, np.random.default_rng(1))

    # --- assert -----------------------
    assert population.tuple_array.shape == (population.u.size, 2)
    assert not np.any(population.u_lane == population.v_lane)
    cells = np.zeros((N_FINE_LANES, N_FINE_LANES), dtype=np.int64)
    np.add.at(cells, (population.u_lane, population.v_lane), 1)
    free_cells = cells[np.ix_(_FREE_LANES, _FREE_LANES)]
    off_diagonal_cells = free_cells[~np.eye(_FREE_LANES.size, dtype=bool)]
    assert off_diagonal_cells.max() - off_diagonal_cells.min() <= 1
    assert off_diagonal_cells.sum() == cells.sum() == population.u.size
    for values, lanes in ((population.u, population.u_lane), (population.v, population.v_lane)):
        assert np.array_equal(fine_lanes_of(values), lanes)
        assert np.all((values > 0) & (values < 0.5))


def test_draw_in_fine_cells_of_puts_each_base_tuple_first_and_its_candidates_inside_its_fine_cell():
    """Each of the 3 base tuples is followed by its 5 candidates, which all lie in its fine cell, at distinct
    positions."""
    # --- arrange ----------------------
    base_tuple_array = np.array([[3.5, 400.25], [10.75, 2.5], [511.5, 255.9]]) / N_FINE_LANES

    # --- act --------------------------
    population = MCTuplesPopulation.draw_in_fine_cells_of(base_tuple_array, 5, np.random.default_rng(2))

    # --- assert -----------------------
    assert population.u.size == 18
    assert np.array_equal(population.tuple_array[::6], base_tuple_array)
    for values, lanes, column in ((population.u, population.u_lane, 0), (population.v, population.v_lane, 1)):
        assert np.array_equal(lanes, np.repeat(fine_lanes_of(base_tuple_array[:, column]), 6))
        assert np.array_equal(fine_lanes_of(values), lanes)
        assert np.unique(values).size == 18


def test_every_drawn_value_and_its_mirror_hold_at_least_min_n_bits():
    """Every value that either population draws holds at least `MIN_N_BITS` bits, and so does its mirror 1 - value,
    which the set also holds; drawn at random, about 1 mirror in 5 holds fewer."""
    # --- arrange ----------------------
    rng = np.random.default_rng(3)
    base_tuple_array = np.array([[3.5, 400.25], [10.75, 2.5]]) / N_FINE_LANES

    # --- act --------------------------
    off_diagonal = MCTuplesPopulation.draw_in_off_diagonal_cells(2000, _FREE_LANES, rng)
    in_fine_cells = MCTuplesPopulation.draw_in_fine_cells_of(base_tuple_array, 500, rng)

    # --- assert -----------------------
    drawn_values = np.concatenate(
        [off_diagonal.u, off_diagonal.v, np.delete(in_fine_cells.tuple_array, np.s_[::501], axis=0).ravel()]
    )
    assert drawn_values.size == 2 * off_diagonal.u.size + 2000
    assert min(n_bits(float(value)) for value in drawn_values) >= MIN_N_BITS
    assert min(n_bits(1.0 - float(value)) for value in drawn_values) >= MIN_N_BITS
