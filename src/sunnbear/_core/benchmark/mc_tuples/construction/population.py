"""`MCTuplesPopulation` holds a size's candidate base tuples, among which max-div picks the size's new base tuples.

A base tuple stands for its 4 tuples (`rotations`). Its u and v lie in the lower-half LHS lanes of a size, those of
[0, 0.5], so it lies in the LHS cell where 2 lower-half LHS lanes cross (`MCTuplesSize`). Each size has 2 populations,
1 per max-div solve:

- the selection's (`draw_in_off_diagonal_cells`), in the LHS cells of the size itself;
- the refinement's (`draw_in_lhs_cells_of`), in the LHS cells of the largest size.

The selection's population is drawn in 3 steps:

1. `spread_evenly_over_grid` picks each candidate's LHS cell at random on the grid whose rows and columns are the given
   LHS lanes, so that every lane and every LHS cell holds the same number of candidates, give or take 1; the
   candidates in diagonal cells, whose u and v share an LHS lane, are then dropped;
2. each candidate lies at its own uniform random position inside its LHS cell;
3. the candidates outside the given tiles are dropped.

The refinement's population lies only in the LHS cells of given base tuples: each base tuple comes first, followed by
`n_random_candidates_per_cell` candidates at uniform random positions inside its LHS cell.

Every value and its mirror, 1 - value, become u values and v values of the set, so both hold at least `MIN_N_BITS`
bits of information (`draw_floats_with_min_n_bits`).

An LHS lane's edges are multiples of 1 / size, and every size is a power of 2, so each edge holds fewer bits than a
drawn value, and no value lands on an edge of any size's LHS lanes.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import MIN_N_BITS, MCTuplesSize
from sunnbear._core.utils.float_bits import draw_floats_with_min_n_bits, n_bits
from sunnbear._core.utils.spread_over_grid import spread_evenly_over_grid


# ==================================================================================================
#  MCTuplesPopulation
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesPopulation:
    """`MCTuplesPopulation` holds the candidate base tuples of 1 size.

    Attributes:
        u: The u value of each candidate, in the open interval (0, 0.5).
        v: The v value of each candidate, in the open interval (0, 0.5).
    """

    u: np.ndarray
    v: np.ndarray

    @property
    def base_tuple_array(self) -> np.ndarray:
        """Return the candidate base tuples as an `(n, 2)` array of (u, v) values."""
        return np.column_stack([self.u, self.v])

    def extended_by(self, other: "MCTuplesPopulation") -> "MCTuplesPopulation":
        """Return this population followed by the candidates of `other`."""
        return MCTuplesPopulation(u=np.concatenate([self.u, other.u]), v=np.concatenate([self.v, other.v]))

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _draw_values_in_lhs_lanes(lane_indices: np.ndarray, size: MCTuplesSize, rng: np.random.Generator) -> np.ndarray:
        """Return 1 random value inside each LHS lane of `size` in `lane_indices`, its mirror included.

        Each value and its mirror, 1 - value, hold at least `MIN_N_BITS` bits.
        """
        lows, highs = size.lhs_lane_edges(lane_indices)
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
    def draw_in_lhs_cells(
        cls, u_lane_indices: np.ndarray, v_lane_indices: np.ndarray, size: MCTuplesSize, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Return 1 candidate at a uniform random position inside each LHS cell of `size` that the 2 lane arrays name.

        Candidate `i` lies in the LHS cell of LHS lane `u_lane_indices[i]` along u and LHS lane `v_lane_indices[i]`
        along v.
        """
        return cls(
            u=cls._draw_values_in_lhs_lanes(u_lane_indices, size, rng),
            v=cls._draw_values_in_lhs_lanes(v_lane_indices, size, rng),
        )

    @classmethod
    def draw_in_off_diagonal_cells(
        cls,
        n_population: int,
        free_lanes: np.ndarray,
        free_tiles: np.ndarray,
        size: MCTuplesSize,
        rng: np.random.Generator,
    ) -> "MCTuplesPopulation":
        """Draw candidates over the off-diagonal LHS cells of `free_lanes`, and keep those that lie in `free_tiles`.

        `free_lanes` are LHS lanes of `size`, and `free_tiles` are tiles of `size`. `n_population` candidates are spread
        evenly over all LHS cells of the grid of `free_lanes`, the diagonal included; those in a diagonal cell are then
        dropped, about `n_population / free_lanes.size` of them, and so are those outside `free_tiles`.
        """
        cells = np.fromiter(
            spread_evenly_over_grid(n_population, free_lanes.size, free_lanes.size, rng),
            dtype=np.dtype((np.int64, 2)),
            count=n_population,
        )
        cells = cells[cells[:, 0] != cells[:, 1]]
        population = cls.draw_in_lhs_cells(free_lanes[cells[:, 0]], free_lanes[cells[:, 1]], size, rng)
        is_in_free_tile = np.isin(size.tile_indices(population.u, population.v), free_tiles)
        return cls(u=population.u[is_in_free_tile], v=population.v[is_in_free_tile])

    @classmethod
    def draw_in_lhs_cells_of(
        cls,
        base_tuple_array: np.ndarray,
        n_random_candidates_per_cell: int,
        size: MCTuplesSize,
        rng: np.random.Generator,
    ) -> "MCTuplesPopulation":
        """Return each base tuple of `base_tuple_array`, followed by random candidates inside its LHS cell of `size`.

        Candidate `i * (n_random_candidates_per_cell + 1)` is the base tuple `i` itself, and the
        `n_random_candidates_per_cell` candidates up to the next base tuple lie at uniform random positions inside the
        LHS cell of `size` of base tuple `i`.
        """
        n_base_tuples = base_tuple_array.shape[0]
        values_per_axis = []
        for values in (base_tuple_array[:, 0], base_tuple_array[:, 1]):
            lanes = np.repeat(size.lhs_lane_indices(values), n_random_candidates_per_cell)
            random_values = cls._draw_values_in_lhs_lanes(lanes, size, rng)
            values_per_axis.append(np.column_stack([values, random_values.reshape(n_base_tuples, -1)]).ravel())
        return cls(u=values_per_axis[0], v=values_per_axis[1])
