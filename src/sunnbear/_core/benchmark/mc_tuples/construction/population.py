"""`MCTuplesPopulation` holds a size's candidate tuples, among which max-div picks the size's new tuples.

Each axis is cut into `N_FINE_LANES` equal fine lanes; a fine cell is the crossing of a fine u-lane and a fine
v-lane.

A size's population is drawn over its eligible fine lanes: the fine lanes of the gaps that its gap allocation gives
new tuples (`MCTuplesAxisGapAllocation.eligible_fine_lanes`). A candidate in any other fine lane could never be
picked, so the whole population is usable. The population guarantees:

- every eligible fine lane holds the same number of candidates, give or take 1, along u and along v;
- every eligible fine cell holds `n // n_cells` or `n // n_cells + 1` candidates, with `n` the population size and
  `n_cells` the number of eligible fine cells.

The population is drawn in 2 steps:

1. `spread_evenly_over_grid` picks each candidate's eligible fine cell, at random under both guarantees, on the
   grid of eligible u-lanes and eligible v-lanes;
2. each candidate lies at its own uniform random position inside its fine cell.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES
from sunnbear._core.utils.spread_over_grid import spread_evenly_over_grid

from .allocation import MCTuplesGapAllocation


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
    def _positions_in_lane(n: int, rng: np.random.Generator) -> np.ndarray:
        """Return `n` uniform random positions inside a fine lane, as fractions of its width in the interval (0, 1).

        `rng.random` can return exactly 0, which would put a candidate on the edge of the unit square in fine lane 0;
        such a draw moves to the middle of the lane.
        """
        positions = rng.random(n)
        positions[positions == 0.0] = 0.5
        return positions

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def draw(
        cls, n_population: int, u_lanes: np.ndarray, v_lanes: np.ndarray, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Draw `n_population` candidates over the fine cells of `u_lanes` x `v_lanes`."""
        candidate_cells = np.fromiter(
            spread_evenly_over_grid(n_population, u_lanes.size, v_lanes.size, rng),
            dtype=np.dtype((np.int64, 2)),
            count=n_population,
        )
        u_lane = u_lanes[candidate_cells[:, 0]].astype(np.int64)
        v_lane = v_lanes[candidate_cells[:, 1]].astype(np.int64)
        return cls(
            u=(u_lane + cls._positions_in_lane(u_lane.size, rng)) / N_FINE_LANES,
            v=(v_lane + cls._positions_in_lane(v_lane.size, rng)) / N_FINE_LANES,
            u_lane=u_lane,
            v_lane=v_lane,
        )

    @classmethod
    def draw_in_eligible_lanes(
        cls, n_population: int, gap_allocation: MCTuplesGapAllocation, rng: np.random.Generator
    ) -> "MCTuplesPopulation":
        """Draw `n_population` candidates over the eligible fine lanes of `gap_allocation`, on both axes."""
        return cls.draw(n_population, gap_allocation.u.eligible_fine_lanes, gap_allocation.v.eligible_fine_lanes, rng)
