"""`MCTuplesPopulation` holds a size's candidate tuples, among which max-div picks the size's new tuples.

Each axis is cut into `N_FINE_LANES` equal fine lanes; a fine cell is the crossing of a fine u-lane and a fine
v-lane. Each size has 2 populations, 1 per max-div solve: the selection's (`draw`) and the refinement's
(`draw_in_fine_cells_of`).

The selection's population is drawn over the size's eligible fine lanes: the fine lanes of the gaps with new tuples
in its gap allocation (`MCTuplesAxisGapAllocation.eligible_fine_lanes`). A candidate in any other fine lane could
never be picked, so the whole population is usable. The selection's population guarantees:

- every eligible fine lane holds the same number of candidates, give or take 1, along u and along v;
- every eligible fine cell, the crossing of an eligible u-lane and an eligible v-lane, holds `n // n_cells` or
  `n // n_cells + 1` candidates, with `n` the population size and `n_cells` the number of eligible fine cells.

The selection's population is drawn in 2 steps:

1. `spread_evenly_over_grid` picks each candidate's eligible fine cell, at random under both guarantees, on the
   grid of eligible u-lanes and eligible v-lanes;
2. each candidate lies at its own uniform random position inside its fine cell, with at least `MIN_N_BITS` bits of
   information in each value (`draw_floats_with_min_n_bits`).

The refinement's population lies only in the fine cells of given tuples: each tuple comes first, followed by
`n_random_candidates_per_cell` candidates at uniform random positions inside its fine cell, drawn in the same way.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import MIN_N_BITS, N_FINE_LANES, fine_lanes_of
from sunnbear._core.utils.float_bits import draw_floats_with_min_n_bits
from sunnbear._core.utils.spread_over_grid import spread_evenly_over_grid


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
    def _values_in_lanes(lanes: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """Return 1 uniform random value strictly inside each fine lane of `lanes`, with at least `MIN_N_BITS` bits.

        A fine lane's edges are dyadic fractions with few bits, so no value lands on an edge, not even on the edge of
        the unit square.
        """
        return draw_floats_with_min_n_bits(lanes / N_FINE_LANES, (lanes + 1) / N_FINE_LANES, MIN_N_BITS, rng)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def draw(
        cls, n_population: int, allowed_u_lanes: np.ndarray, allowed_v_lanes: np.ndarray, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Draw `n_population` candidates over the fine cells of `allowed_u_lanes` x `allowed_v_lanes`."""
        candidate_cells = np.fromiter(
            spread_evenly_over_grid(n_population, allowed_u_lanes.size, allowed_v_lanes.size, rng),
            dtype=np.dtype((np.int64, 2)),
            count=n_population,
        )
        u_lane = allowed_u_lanes[candidate_cells[:, 0]].astype(np.int64)
        v_lane = allowed_v_lanes[candidate_cells[:, 1]].astype(np.int64)
        return cls(
            u=cls._values_in_lanes(u_lane, rng),
            v=cls._values_in_lanes(v_lane, rng),
            u_lane=u_lane,
            v_lane=v_lane,
        )

    @classmethod
    def draw_in_fine_cells_of(
        cls, tuple_array: np.ndarray, n_random_candidates_per_cell: int, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Return each tuple of `tuple_array`, followed by random candidates inside its fine cell.

        Candidate `i * (n_random_candidates_per_cell + 1)` is the tuple `i` itself, and the
        `n_random_candidates_per_cell` candidates up to the next tuple lie at uniform random positions inside the fine
        cell of tuple `i`.
        """
        n_tuples = tuple_array.shape[0]
        values_per_axis, lanes_per_axis = [], []
        for values in (tuple_array[:, 0], tuple_array[:, 1]):
            lanes = fine_lanes_of(values)
            random_values = cls._values_in_lanes(np.repeat(lanes, n_random_candidates_per_cell), rng)
            values_per_axis.append(np.column_stack([values, random_values.reshape(n_tuples, -1)]).ravel())
            lanes_per_axis.append(np.repeat(lanes, n_random_candidates_per_cell + 1))
        return cls(u=values_per_axis[0], v=values_per_axis[1], u_lane=lanes_per_axis[0], v_lane=lanes_per_axis[1])
