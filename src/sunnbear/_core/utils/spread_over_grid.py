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

    Which `n_items % n_cells` cells hold 1 more is drawn at random, but not uniformly over all placements of the extra
    items that give these row and column counts. The cells come row by row, with the rows in random order.

    The generator draws from `rng` while it is iterated, so drawing other values from `rng` before it yields its last
    cell changes which cells it yields.
    """
    n_per_cell, n_extra = divmod(n_items, n_rows * n_cols)

    # --- extra items per row and column ---------
    # Every row and every column gets its number of extra items, the items beyond `n_per_cell` in its cells: equal up
    # to 1, with the rows and columns that get 1 more picked at random.
    n_extra_per_row, n_extra_left_per_col = np.full(n_rows, n_extra // n_rows), np.full(n_cols, n_extra // n_cols)
    for counts in (n_extra_per_row, n_extra_left_per_col):
        counts[rng.choice(counts.size, size=n_extra % counts.size, replace=False)] += 1

    # --- extra cells per row --------------------
    # The rows, in random order, each put their extra items in the distinct columns with the most extra items left to
    # place.
    #
    # A random pick among the columns with extra items left can leave a later row with fewer such columns than it has
    # extra items to place. Taking the columns with the most left never does: whenever a 0/1 grid with these row and
    # column counts exists, this choice finds one (the constructive proof of the Gale-Ryser theorem), and with counts
    # equal up to 1 such a grid always exists.
    for i in rng.permutation(n_rows):
        # Sort the columns by their extra items left to place, most first; the random keys break ties at random.
        cols_with_extra = np.lexsort((rng.random(n_cols), -n_extra_left_per_col))[: n_extra_per_row[i]]
        n_extra_left_per_col[cols_with_extra] -= 1
        n_in_cell_of_row = np.full(n_cols, n_per_cell)
        n_in_cell_of_row[cols_with_extra] += 1
        for j in np.repeat(np.arange(n_cols), n_in_cell_of_row):
            yield int(i), int(j)
