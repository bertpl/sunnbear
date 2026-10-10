"""`spread_evenly_over_grid` spreads items at random over a grid, as evenly over cells, rows and columns as it can."""

import numpy as np
import pytest

from sunnbear._core.utils.grid_spread import spread_evenly_over_grid


def _items_per_cell(n_items: int, n_rows: int, n_cols: int, seed: int) -> np.ndarray:
    """Return the `(n_rows, n_cols)` array of the number of items that 1 call of `spread_evenly_over_grid` puts in each
    cell."""
    cells = np.array(list(spread_evenly_over_grid(n_items, n_rows, n_cols, np.random.default_rng(seed))))
    n_in_cell = np.zeros((n_rows, n_cols), dtype=np.int64)
    np.add.at(n_in_cell, (cells[:, 0], cells[:, 1]), 1)
    return n_in_cell


@pytest.mark.parametrize(
    "n_items, n_rows, n_cols",
    [
        (
            3,
            2,
            2,
        ),  # a grid on which a random pick among the columns with extra items left to place can run out of columns
        (250, 20, 30),  # fewer items than cells: at most 1 per cell
        (3 * 20 * 30 + 77, 20, 30),  # 3 or 4 per cell
        (
            458_752,
            768,
            768,
        ),  # 597 or 598 extra items in each row of 768 cells, the densest case of the MC tuple construction
    ],
)
def test_spread_evenly_over_grid_balances_every_cell_row_and_column(n_items, n_rows, n_cols):
    """Every cell, every row and every column holds the same number of items, give or take 1."""
    # --- act --------------------------
    n_in_cell = _items_per_cell(n_items, n_rows, n_cols, seed=1)

    # --- assert -----------------------
    assert n_in_cell.sum() == n_items
    for counts in (n_in_cell, n_in_cell.sum(axis=1), n_in_cell.sum(axis=0)):
        assert counts.max() - counts.min() <= 1


def test_spread_evenly_over_grid_draws_a_different_spread_per_seed():
    """The seeds 1 and 2 put the items in different cells."""
    # --- act / assert -----------------
    assert not np.array_equal(_items_per_cell(250, 20, 30, seed=1), _items_per_cell(250, 20, 30, seed=2))
