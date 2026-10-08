"""`MCTuplesPopulation` holds the candidate tuples that max-div picks a size's new tuples from.

Each axis is cut into `N_FINE_LANES` equal fine lanes; a fine cell is the crossing of a fine u-lane and a fine
v-lane. A size's population is drawn over the fine lanes that the size below leaves free, and guarantees:

- every free fine lane holds the same number of candidates, up to 1, along u and along v;
- every free fine cell holds the same number of candidates, up to 1: at most 1 while the population is no larger than
  the number of free fine cells, and `n // n_cells` or 1 more above it.

Every free fine cell first gets `n // n_cells` candidates. Which cells get 1 of the remaining `n % n_cells` is drawn
at random under both guarantees: a round-robin pattern fills the free u-lanes one after the other, each continuing
cyclically over the free v-lanes where the previous one stopped, and curveball trades then randomize that pattern.
Each candidate lies at its own uniform random position inside its fine cell.
"""

from dataclasses import dataclass

import numpy as np

from .sizes import N_FINE_LANES

# Curveball trades per free fine u-lane: each trade involves 2 lanes, so every lane takes part in about twice this many.
N_CURVEBALL_TRADES_PER_LANE = 100


# ==================================================================================================
#  MCTuplesPopulation
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesPopulation:
    """`MCTuplesPopulation` holds the candidate tuples of 1 size, with each candidate's fine lanes.

    Attributes:
        u: The u value of each candidate, in the open interval (0, 1).
        v: The v value of each candidate, in the open interval (0, 1).
        u_lane: The fine u-lane of each candidate.
        v_lane: The fine v-lane of each candidate.
    """

    u: np.ndarray
    v: np.ndarray
    u_lane: np.ndarray
    v_lane: np.ndarray

    @property
    def tuple_array(self) -> np.ndarray:
        """Return the candidates as an `(n, 2)` array of (u, v) values."""
        return np.column_stack([self.u, self.v])

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _round_robin_pattern(n_rows: int, n_cols: int, n_occupied: int, rng: np.random.Generator) -> np.ndarray:
        """Return an `(n_rows, n_cols)` pattern of `n_occupied` cells, with row and column counts equal up to 1.

        `n_occupied % n_rows` random rows hold 1 more than the others. Each row's cells continue cyclically over the
        columns where the previous row's stopped, so the cells cover the positions 0 to `n_occupied - 1` of the cycle
        once each, and every column gets the same count up to 1; a random column permutation then decides which
        columns get the extra 1.
        """
        row_counts = np.full(n_rows, n_occupied // n_rows)
        row_counts[rng.choice(n_rows, size=n_occupied % n_rows, replace=False)] += 1
        starts = np.concatenate([[0], np.cumsum(row_counts)[:-1]])
        is_occupied = np.zeros((n_rows, n_cols), dtype=bool)
        for row, (start, count) in enumerate(zip(starts, row_counts, strict=True)):
            is_occupied[row, (start + np.arange(count)) % n_cols] = True
        return is_occupied[:, rng.permutation(n_cols)]

    @staticmethod
    def _randomize_pattern(is_occupied: np.ndarray, n_trades: int, rng: np.random.Generator) -> None:
        """Apply `n_trades` curveball trades to the rows of `is_occupied`, in place.

        A trade picks 2 distinct rows, pools the columns that hold a candidate in exactly 1 of the 2, shuffles the
        pool and deals it back in the same counts. A trade keeps every row's and every column's count and never puts
        2 candidates in 1 cell; enough trades make the pattern a uniform draw from all such patterns.
        """
        n_rows = is_occupied.shape[0]
        rows_a = rng.integers(0, n_rows, size=n_trades)
        rows_b = (rows_a + rng.integers(1, n_rows, size=n_trades)) % n_rows
        for row_a_index, row_b_index in zip(rows_a, rows_b, strict=True):
            row_a, row_b = is_occupied[row_a_index], is_occupied[row_b_index]  # views into is_occupied
            differing = np.flatnonzero(row_a ^ row_b)
            n_in_a = int(row_a[differing].sum())
            dealt = rng.permutation(differing)
            row_a[differing] = False
            row_b[differing] = False
            row_a[dealt[:n_in_a]] = True
            row_b[dealt[n_in_a:]] = True

    @staticmethod
    def _offsets(n: int, rng: np.random.Generator) -> np.ndarray:
        """Return `n` uniform random offsets inside a fine lane, as fractions of its width in the open interval (0, 1).

        `rng.random` can return exactly 0, which would put a candidate on the edge of the unit square in fine lane 0;
        such a draw moves to the middle of the lane.
        """
        offsets = rng.random(n)
        offsets[offsets == 0.0] = 0.5
        return offsets

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def draw(
        cls, n_candidates: int, free_u_lanes: np.ndarray, free_v_lanes: np.ndarray, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Draw `n_candidates` candidates over the fine cells of `free_u_lanes` × `free_v_lanes`.

        Raises:
            ValueError: If `n_candidates` is not positive.
        """
        if n_candidates < 1:
            raise ValueError(f"n_candidates must be positive (got {n_candidates}).")
        n_rows, n_cols = free_u_lanes.size, free_v_lanes.size
        n_per_cell, n_extra = divmod(n_candidates, n_rows * n_cols)
        is_extra = cls._round_robin_pattern(n_rows, n_cols, n_extra, rng)
        # With no extra candidates every free fine cell holds the same number, so there is nothing to randomize.
        n_trades = N_CURVEBALL_TRADES_PER_LANE * n_rows if n_extra > 0 else 0
        cls._randomize_pattern(is_extra, n_trades, rng)
        n_in_cell = n_per_cell + is_extra.astype(np.int64)
        rows, cols = np.nonzero(n_in_cell)
        repeats = n_in_cell[rows, cols]
        rows, cols = np.repeat(rows, repeats), np.repeat(cols, repeats)
        u_lane, v_lane = free_u_lanes[rows].astype(np.int64), free_v_lanes[cols].astype(np.int64)
        return cls(
            u=(u_lane + cls._offsets(u_lane.size, rng)) / N_FINE_LANES,
            v=(v_lane + cls._offsets(v_lane.size, rng)) / N_FINE_LANES,
            u_lane=u_lane,
            v_lane=v_lane,
        )
