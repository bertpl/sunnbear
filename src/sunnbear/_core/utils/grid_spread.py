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

    Every cell first gets `n_items // n_cells` items. Which `n_items % n_cells` cells get 1 more is drawn at random in
    2 steps:

    1. every row and every column gets its number of extra items: equal up to 1, with the ones that get 1 more picked
       at random;
    2. the rows, in random order, each put their extra items in distinct columns: the columns with the most extra
       items left to place, ties broken at random. A random pick among all columns with room left would run out of
       columns near the last rows; this rule never does, because a cell pattern with these row and column counts
       always exists (the constructive proof of the Gale-Ryser theorem).

    The cells come row by row, in the random order of step 2.
    """
    n_per_cell, n_extra = divmod(n_items, n_rows * n_cols)

    # --- extra items per row and column ---------
    row_counts, col_room = np.full(n_rows, n_extra // n_rows), np.full(n_cols, n_extra // n_cols)
    for counts in (row_counts, col_room):
        counts[rng.choice(counts.size, size=n_extra % counts.size, replace=False)] += 1

    # --- extra cells per row --------------------
    for i in rng.permutation(n_rows):
        # The columns sorted by room left, most first; the random keys break ties at random.
        extra_cols = np.lexsort((rng.random(n_cols), -col_room))[: row_counts[i]]
        col_room[extra_cols] -= 1
        n_in_cell = np.full(n_cols, n_per_cell)
        n_in_cell[extra_cols] += 1
        for j in range(n_cols):
            for _ in range(n_in_cell[j]):
                yield int(i), j
