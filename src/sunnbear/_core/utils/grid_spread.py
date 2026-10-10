"""This module spreads items at random over the cells of a grid, as evenly as the grid allows."""

from collections.abc import Iterator

import numpy as np


def spread_evenly_over_grid(
    n_items: int, n_rows: int, n_cols: int, rng: np.random.Generator
) -> Iterator[tuple[int, int]]:
    """Yield the cell `(i, j)` of each of `n_items` items on an `n_rows` x `n_cols` grid, with `i` the row.

    The spread is as even as the grid allows:

    - every cell holds `n_items // n_cells` or 1 more items, with `n_cells = n_rows * n_cols`;
    - every row holds the same number of items, give or take 1, and so does every column.

    Which `n_items % n_cells` cells hold 1 more is drawn at random, but not uniformly over all patterns with these row
    and column counts. The cells come row by row, with the rows in random order.

    The generator draws from `rng` as it is iterated, so other draws from `rng` before the last cell change the cells.
    """
    n_per_cell, n_extra = divmod(n_items, n_rows * n_cols)

    # --- extra items per row and column ---------
    # Every row and every column gets its number of extra items: equal up to 1, with the rows and columns that get 1
    # more picked at random.
    n_extra_per_row, n_extra_left_per_col = np.full(n_rows, n_extra // n_rows), np.full(n_cols, n_extra // n_cols)
    for counts in (n_extra_per_row, n_extra_left_per_col):
        counts[rng.choice(counts.size, size=n_extra % counts.size, replace=False)] += 1

    # --- extra cells per row --------------------
    # The rows, in random order, each put their extra items in the distinct columns with the most extra items left to
    # place. A random pick among all columns with extra items left to place would run out of columns near the last
    # rows; taking the columns with the most left never does, because a cell pattern with these row and column counts
    # always exists (the constructive proof of the Gale-Ryser theorem).
    for i in rng.permutation(n_rows):
        # Sort the columns by their extra items left to place, most first; the random keys break ties at random.
        extra_cols = np.lexsort((rng.random(n_cols), -n_extra_left_per_col))[: n_extra_per_row[i]]
        n_extra_left_per_col[extra_cols] -= 1
        n_in_row_cells = np.full(n_cols, n_per_cell)
        n_in_row_cells[extra_cols] += 1
        for j in range(n_cols):
            for _ in range(n_in_row_cells[j]):
                yield int(i), j
