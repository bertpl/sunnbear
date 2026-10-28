"""`MCTuplesPopulation` holds a size's candidate base tuples, among which max-div picks the size's new base tuples.

A base tuple stands for its 4 tuples (`rotations`). Its u and v lie in the lower fine lanes, those of [0, 0.5], so its
fine cell is the crossing of 2 lower fine lanes. Each size has 2 populations, 1 per max-div solve: the selection's
(`draw_in_off_diagonal_cells`) and the refinement's (`draw_in_fine_cells_of`).

The selection's population lies in the fine cells of the lower fine lanes that the size below leaves free, except the
diagonal cells, whose u and v share a fine lane.
A candidate in any other fine cell could never be picked:

- a lane that the size below uses would hold 2 values;
- a diagonal cell holds u and v in 1 fine lane, which would put 2 tuples in 1 fine lane on each axis.

The selection's population is drawn in 2 steps:

1. `spread_evenly_over_grid` picks each candidate's fine cell at random on the grid whose rows and columns are the free
   lanes, so that every free lane and every fine cell holds the same number of candidates, give or take 1; the
   candidates in diagonal cells are then dropped;
2. each candidate lies at its own uniform random position inside its fine cell.

The refinement's population lies only in the fine cells of given base tuples: each base tuple comes first, followed by
`n_random_candidates_per_cell` candidates at uniform random positions inside its fine cell.

Every value and its mirror, 1 - value, become u values and v values of the set, so both hold at least `MIN_N_BITS`
bits of information (`draw_floats_with_min_n_bits`).

A fine lane's edges are multiples of 1 / `N_FINE_LANES`, and `N_FINE_LANES` is a power of 2, so each edge holds fewer
bits than a drawn value, and no value lands on an edge.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import MIN_N_BITS, fine_lane_edges_of, fine_lanes_of
from sunnbear._core.utils.float_bits import draw_floats_with_min_n_bits, n_bits
from sunnbear._core.utils.spread_over_grid import spread_evenly_over_grid


# ==================================================================================================
#  MCTuplesPopulation
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesPopulation:
    """`MCTuplesPopulation` holds the candidate base tuples of 1 size, with each candidate's fine lanes.

    Attributes:
        u: The u value of each candidate, in the open interval (0, 0.5).
        v: The v value of each candidate, in the open interval (0, 0.5).
        u_lane: The fine u-lane of each candidate, a lower fine lane.
        v_lane: The fine v-lane of each candidate, a lower fine lane.
    """

    u: np.ndarray
    v: np.ndarray
    u_lane: np.ndarray
    v_lane: np.ndarray

    @property
    def base_tuple_array(self) -> np.ndarray:
        """Return the candidate base tuples as an `(n, 2)` array of (u, v) values."""
        return np.column_stack([self.u, self.v])

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _draw_values_in_fine_lanes(lanes: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """Return 1 random value inside each fine lane in `lanes`, with `MIN_N_BITS` bits in it and in its mirror."""
        lows, highs = fine_lane_edges_of(lanes)
        values = draw_floats_with_min_n_bits(lows, highs, MIN_N_BITS, rng)
        to_check = np.arange(values.size)
        while to_check.size > 0:
            has_too_few_bits = np.array(
                [n_bits(1.0 - float(values[i])) < MIN_N_BITS for i in to_check.tolist()], dtype=bool
            )
            to_check = to_check[has_too_few_bits]
            values[to_check] = draw_floats_with_min_n_bits(lows[to_check], highs[to_check], MIN_N_BITS, rng)
        return values

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def draw_in_off_diagonal_cells(
        cls, n_population: int, free_lanes: np.ndarray, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Draw candidates over the off-diagonal fine cells of the grid whose rows and columns are `free_lanes`.

        `n_population` candidates are spread evenly over all fine cells of the grid, the diagonal included; those in a
        diagonal cell are then dropped, about `n_population / free_lanes.size` of them.
        """
        cells = np.fromiter(
            spread_evenly_over_grid(n_population, free_lanes.size, free_lanes.size, rng),
            dtype=np.dtype((np.int64, 2)),
            count=n_population,
        )
        cells = cells[cells[:, 0] != cells[:, 1]]
        u_lane = free_lanes[cells[:, 0]].astype(np.int64)
        v_lane = free_lanes[cells[:, 1]].astype(np.int64)
        return cls(
            u=cls._draw_values_in_fine_lanes(u_lane, rng),
            v=cls._draw_values_in_fine_lanes(v_lane, rng),
            u_lane=u_lane,
            v_lane=v_lane,
        )

    @classmethod
    def draw_in_fine_cells_of(
        cls, base_tuple_array: np.ndarray, n_random_candidates_per_cell: int, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Return each base tuple of `base_tuple_array`, followed by random candidates inside its fine cell.

        Candidate `i * (n_random_candidates_per_cell + 1)` is the base tuple `i` itself, and the
        `n_random_candidates_per_cell` candidates up to the next base tuple lie at uniform random positions inside the
        fine cell of base tuple `i`.
        """
        n_base_tuples = base_tuple_array.shape[0]
        values_per_axis, lanes_per_axis = [], []
        for values in (base_tuple_array[:, 0], base_tuple_array[:, 1]):
            lanes = fine_lanes_of(values)
            random_values = cls._draw_values_in_fine_lanes(np.repeat(lanes, n_random_candidates_per_cell), rng)
            values_per_axis.append(np.column_stack([values, random_values.reshape(n_base_tuples, -1)]).ravel())
            lanes_per_axis.append(np.repeat(lanes, n_random_candidates_per_cell + 1))
        return cls(u=values_per_axis[0], v=values_per_axis[1], u_lane=lanes_per_axis[0], v_lane=lanes_per_axis[1])
