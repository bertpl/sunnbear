"""`MCTuplesGapAllocation` decides how many of a size's new tuples go into each gap left by the size below.

On each axis, every tuple of the size below occupies 1 fine lane. A gap is a maximal run of free fine lanes: between 2
occupied fine lanes, or between an occupied fine lane and an edge of the axis (`MCTuplesAxisGaps`).

The size's max-div solve puts exactly the allocated number of new tuples into each gap, and spreads them about evenly
inside it. So the allocation sets where the size's mean lies, and with it how far the mean correction has to move the
new tuples.

The allocation comes in 2 stages:

1. **greedy:** the new tuples go to the gaps 1 at a time, each to the gap that has the widest spacing after it takes
   the tuple; a gap's spacing is the distance between its neighboring values once its new tuples are spread evenly
   over it;
2. **mean-aware:** starting from the greedy allocation, a local search moves new tuples between gaps, 1 at a time, to
   raise a score: the predicted smallest spacing minus the absolute predicted offset of the size's mean from 0.5,
   both in fine lanes (`MCTuplesAxisGaps.predicted_score`). The score estimates the smallest spacing that remains
   once the mean correction has removed the offset, so the search gives up spacing only where it buys a larger
   reduction of the offset.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES, TARGET_MEAN, fine_lanes_of


# ==================================================================================================
#  MCTuplesGapAllocation
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesGapAllocation:
    """`MCTuplesGapAllocation` holds, for 1 size, the allocation of its new tuples to the gaps along u and along v.

    Attributes:
        u: The allocation along u.
        v: The allocation along v.
    """

    u: "MCTuplesAxisGapAllocation"
    v: "MCTuplesAxisGapAllocation"

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, required_tuple_array: np.ndarray, n_new: int) -> "MCTuplesGapAllocation":
        """Return the mean-aware allocation of `n_new` new tuples along u and along v of `required_tuple_array`."""
        return cls(
            u=MCTuplesAxisGapAllocation.of(required_tuple_array[:, 0], n_new),
            v=MCTuplesAxisGapAllocation.of(required_tuple_array[:, 1], n_new),
        )


# ==================================================================================================
#  MCTuplesAxisGapAllocation
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesAxisGapAllocation:
    """`MCTuplesAxisGapAllocation` holds the allocation chosen for 1 axis of 1 size, in the form that the solve uses.

    `MCTuplesAxisGaps` describes every gap and computes the allocation; `MCTuplesAxisGapAllocation` keeps only the
    gaps that get new tuples, how many each gets, and the predicted offsets for the progress report.

    Attributes:
        gap_of_fine_lane: For each fine lane, the gap that holds it, numbered from 0 in ascending order among the gaps
            that get new tuples, or -1 for an occupied fine lane or one in a gap that gets none.
        counts: The number of new tuples of each gap that gets any.
        greedy_offset_fine_lanes: The predicted offset of the size's mean from 0.5 under the greedy allocation, in
            fine lanes; `None` for the smallest size, whose axis is 1 gap of all fine lanes.
        mean_aware_offset_fine_lanes: The same under the mean-aware allocation, which `counts` holds.
    """

    gap_of_fine_lane: np.ndarray
    counts: np.ndarray
    greedy_offset_fine_lanes: float | None
    mean_aware_offset_fine_lanes: float | None

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, required_values: np.ndarray, n_new: int) -> "MCTuplesAxisGapAllocation":
        """Return the mean-aware allocation of `n_new` new tuples over the gaps that `required_values` leave free.

        Without tuples of a size below, all fine lanes form 1 gap that gets every new tuple.
        """
        if required_values.size == 0:
            return cls(
                gap_of_fine_lane=np.zeros(N_FINE_LANES, dtype=np.int64),
                counts=np.array([n_new]),
                greedy_offset_fine_lanes=None,
                mean_aware_offset_fine_lanes=None,
            )
        else:
            gaps = MCTuplesAxisGaps.of(required_values)
            greedy_counts = gaps.greedy_counts(n_new)
            counts = gaps.mean_aware_counts(greedy_counts)
            is_used = counts > 0
            return cls(
                gap_of_fine_lane=gaps.gap_of_fine_lane(is_used),
                counts=counts[is_used],
                greedy_offset_fine_lanes=gaps.predicted_offset_fine_lanes(greedy_counts),
                mean_aware_offset_fine_lanes=gaps.predicted_offset_fine_lanes(counts),
            )


# ==================================================================================================
#  MCTuplesAxisGaps
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesAxisGaps:
    """`MCTuplesAxisGaps` describes the gaps that the size below leaves on 1 axis and allocates new tuples to them.

    It holds every gap, including those that end up without new tuples, and exists only inside
    `MCTuplesAxisGapAllocation.of`, which keeps the result.

    Every attribute except `n_required` and `required_sum` is an array with 1 entry per gap, in ascending order, so
    that each step of an allocation scores every gap at once.

    A gap's width counts fine lanes by their indices, not the distance between the tuples' values: an interior gap
    between occupied fine lanes `a` and `b` is `b - a` wide; a left edge gap below occupied fine lane `b` is `b` wide,
    and a right edge gap above `a` is `N_FINE_LANES - 1 - a` wide, because the outermost new tuple can lie in the
    outermost fine lane.

    Attributes:
        first_lanes: The first free fine lane of each gap, ascending.
        n_free_lanes: The number of free fine lanes of each gap, the most new tuples it can hold.
        widths: The width of each gap, in fine lanes.
        is_left_edge: Whether each gap starts at the left edge of the axis, at 0.
        is_right_edge: Whether each gap ends at the right edge of the axis, at 1.
        lows: The lower bound of each gap on the axis: the value of the tuple below it, or 0 for the left edge gap.
        highs: The upper bound of each gap on the axis: the value of the tuple above it, or 1 for the right edge gap.
        n_required: The number of tuples of the size below.
        required_sum: The sum of their values on this axis.
    """

    first_lanes: np.ndarray
    n_free_lanes: np.ndarray
    widths: np.ndarray
    is_left_edge: np.ndarray
    is_right_edge: np.ndarray
    lows: np.ndarray
    highs: np.ndarray
    n_required: int
    required_sum: float

    # --------------------------------------------------------------------------
    #  Predictions
    # --------------------------------------------------------------------------
    def spacings(self, counts: np.ndarray) -> np.ndarray:
        """Return each gap's spacing, in fine lanes, with its `counts` new tuples spread evenly over it.

        An interior gap's c new tuples split it into c + 1 equal parts, and an edge gap's into c, since its outermost
        tuple lies on the edge; an empty gap has no spacing of its own and gets inf.
        """
        n_parts = np.where(self.is_left_edge | self.is_right_edge, counts, counts + 1)
        return np.divide(self.widths, n_parts, out=np.full(self.widths.shape, np.inf), where=counts > 0)

    def predicted_sums(self, counts: np.ndarray) -> np.ndarray:
        """Return each gap's predicted sum of new values, with its `counts` new tuples spread evenly over it.

        In an interior gap the values lie at lows + j·(highs - lows)/(c + 1), j = 1…c, and sum to c times the gap's
        middle. In an edge gap the outermost value lies on the edge: the left edge gap's values lie at
        highs - j·highs/c, and the right edge gap's at lows + j·(1 - lows)/c.
        """
        interior = counts * (self.lows + self.highs) / 2
        left_edge = (counts - 1) * self.highs / 2
        right_edge = counts * self.lows + (counts + 1) * (self.highs - self.lows) / 2
        sums = np.where(self.is_left_edge, left_edge, np.where(self.is_right_edge, right_edge, interior))
        return np.where(counts > 0, sums, 0.0)

    def predicted_offset_fine_lanes(self, counts: np.ndarray) -> float:
        """Return the predicted offset of the size's mean from 0.5, in fine lanes, for the allocation `counts`."""
        size = self.n_required + int(counts.sum())
        mean = (self.required_sum + self.predicted_sums(counts).sum()) / size
        return float((mean - TARGET_MEAN) * N_FINE_LANES)

    def predicted_score(self, counts: np.ndarray) -> float:
        """Return the score of the allocation `counts`: its smallest spacing minus its absolute offset, in fine lanes.

        Both come from the predicted spread of the new tuples (`spacings`, `predicted_offset_fine_lanes`), and the
        score estimates the smallest spacing that remains once the mean correction has removed the offset.
        """
        return float(self.spacings(counts).min() - abs(self.predicted_offset_fine_lanes(counts)))

    # --------------------------------------------------------------------------
    #  Allocations
    # --------------------------------------------------------------------------
    def greedy_counts(self, n_new: int) -> np.ndarray:
        """Return the greedy allocation of `n_new` new tuples: each to the gap that keeps the widest spacing after it.

        A gap takes at most 1 new tuple per free fine lane.
        """
        counts = np.zeros(self.n_free_lanes.size, dtype=np.int64)
        for _ in range(n_new):
            spacing_after_addition = self.spacings(counts + 1)
            spacing_after_addition[counts >= self.n_free_lanes] = -np.inf
            counts[np.argmax(spacing_after_addition)] += 1
        return counts

    def mean_aware_counts(self, greedy_counts: np.ndarray) -> np.ndarray:
        """Return the allocation with a locally best `predicted_score`, reached from `greedy_counts` by single moves.

        The search repeatedly moves 1 new tuple from 1 gap to another, taking the move that raises the score most, and
        stops once no move raises it. A gap takes at most 1 new tuple per free fine lane. Every move raises the score
        strictly, and there are finitely many allocations, so the search ends.
        """
        size = self.n_required + int(greedy_counts.sum())
        target_sum = TARGET_MEAN * size - self.required_sum
        counts = greedy_counts.copy()
        score = self.predicted_score(counts)
        while True:
            # --- the score after each move ------
            sums = self.predicted_sums(counts)
            excess = sums.sum() - target_sum
            removal = sums - self.predicted_sums(counts - 1)
            addition = self.predicted_sums(counts + 1) - sums
            offset_after = np.abs(excess - removal[:, None] + addition[None, :]) / size * N_FINE_LANES
            is_valid = (counts >= 1)[:, None] & (counts < self.n_free_lanes)[None, :]
            np.fill_diagonal(is_valid, False)
            score_after = np.where(is_valid, self._min_spacing_after_moves(counts) - offset_after, -np.inf)

            # --- the best move ------------------
            source, destination = np.unravel_index(np.argmax(score_after), score_after.shape)
            moved_counts = counts.copy()
            moved_counts[source] -= 1
            moved_counts[destination] += 1
            # The score of the move is recomputed from its allocation, so that rounding in the update above cannot
            # make 2 allocations with the same score each look better than the other, and the search cannot cycle.
            if is_valid[source, destination]:
                moved_score = self.predicted_score(moved_counts)
            else:
                moved_score = -np.inf
            if moved_score > score:
                counts, score = moved_counts, moved_score
            else:
                return counts

    # --------------------------------------------------------------------------
    #  Fine lanes
    # --------------------------------------------------------------------------
    def gap_of_fine_lane(self, is_used: np.ndarray) -> np.ndarray:
        """Return each fine lane's gap, numbered from 0 among the gaps in `is_used`, or -1 for a lane outside them."""
        gap_of_fine_lane = np.full(N_FINE_LANES, -1, dtype=np.int64)
        for gap, (first, n_free) in enumerate(zip(self.first_lanes[is_used], self.n_free_lanes[is_used], strict=True)):
            gap_of_fine_lane[first : first + n_free] = gap
        return gap_of_fine_lane

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _min_spacing_after_moves(self, counts: np.ndarray) -> np.ndarray:
        """Return, for each move of 1 new tuple from gap `s` to gap `d`, the smallest spacing after it, at `[s, d]`.

        A move changes the spacings of `s` and `d` only, so the smallest spacing after it is the smallest of those 2
        and of the smallest spacing among the other gaps, which is 1 of the 3 smallest spacings before the move.
        """
        spacings = self.spacings(counts)
        n_gaps = spacings.size
        lowest = np.argsort(spacings)[:3]
        gap = np.arange(n_gaps)
        # Each entry starts at the 3rd smallest spacing, then takes the 2nd and the 1st where they belong to neither gap
        # of the move.
        others_min = np.full((n_gaps, n_gaps), spacings[lowest[2]] if n_gaps >= 3 else np.inf)
        for rank in reversed(range(min(2, n_gaps))):
            is_other = (gap[:, None] != lowest[rank]) & (gap[None, :] != lowest[rank])
            others_min = np.where(is_other, spacings[lowest[rank]], others_min)
        return np.minimum(
            others_min, np.minimum(self.spacings(counts - 1)[:, None], self.spacings(counts + 1)[None, :])
        )

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, required_values: np.ndarray) -> "MCTuplesAxisGaps":
        """Return the gaps that the size below's values on this axis leave free; `required_values` holds at least 1."""
        occupied = np.unique(fine_lanes_of(required_values))
        value_of_fine_lane = np.zeros(N_FINE_LANES)
        value_of_fine_lane[fine_lanes_of(required_values)] = required_values
        lane_below = np.concatenate([[-1], occupied])
        lane_above = np.concatenate([occupied, [N_FINE_LANES]])
        n_free = lane_above - lane_below - 1
        is_gap = n_free > 0
        lane_below, lane_above, n_free = lane_below[is_gap], lane_above[is_gap], n_free[is_gap]
        is_left_edge = lane_below == -1
        is_right_edge = lane_above == N_FINE_LANES
        widths = np.where(
            is_left_edge, lane_above, np.where(is_right_edge, N_FINE_LANES - 1 - lane_below, lane_above - lane_below)
        )
        return cls(
            first_lanes=lane_below + 1,
            n_free_lanes=n_free,
            widths=widths.astype(np.float64),
            is_left_edge=is_left_edge,
            is_right_edge=is_right_edge,
            lows=np.where(is_left_edge, 0.0, value_of_fine_lane[np.maximum(lane_below, 0)]),
            highs=np.where(is_right_edge, 1.0, value_of_fine_lane[np.minimum(lane_above, N_FINE_LANES - 1)]),
            n_required=required_values.size,
            required_sum=float(required_values.sum()),
        )
