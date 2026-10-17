"""`MCTuplesGapAllocation` decides how many of a size's new tuples go into each gap left by the size below.

On each axis, every tuple of the size below occupies 1 fine lane. A gap is a maximal run of free fine lanes: between 2
occupied fine lanes, or between an occupied fine lane and an edge of the axis (`MCTuplesAxisGaps`). The 2 edge gaps are
the 2 parts of 1 gap on the circle on which the solves measure their distances, so the `placement` module places their
new tuples together, while each keeps its own count.

The size's max-div solve puts exactly the allocated number of new tuples into each gap, and spreads them about evenly
inside it. So the allocation sets where the size's mean lies, and with it how far the first value correction, which runs
right after the selection solve, has to move the new tuples.

The allocation comes in 2 stages:

1. **greedy:** the new tuples go to the gaps 1 at a time, each to the gap that has the widest spacing after it takes
   the tuple; a gap's spacing is the distance between neighboring values once its new tuples are spread evenly
   over it, and an edge gap's spacing is that of the whole wrap-around gap, as `MCTuplesAxisGapPlacement` in the
   `placement` module places them;
2. **mean-aware:** starting from the greedy allocation, a local search moves new tuples between gaps, 1 at a time, to
   raise the predicted smallest spacing after the first value correction
   (`MCTuplesAxisGapPlacement.corrected_min_spacing`):
   - the estimate is the predicted smallest spacing minus the absolute predicted offset of the size's mean from 0.5,
     both in fine lanes, with the offset weighted by `MCTuplesAxisGapPlacement.offset_weight`;
   - so the search accepts a smaller smallest spacing only where the weighted offset shrinks by more than the spacing
     does.
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES, fine_lanes_of

from .placement import MCTuplesAxisGapPlacement


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

    @property
    def eligible_fine_lanes(self) -> np.ndarray:
        """Return, in ascending order, the eligible fine lanes: the free fine lanes of the gaps that get new tuples."""
        return np.flatnonzero(self.gap_of_fine_lane >= 0)

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
                greedy_offset_fine_lanes=MCTuplesAxisGapPlacement(gaps, greedy_counts).offset_fine_lanes,
                mean_aware_offset_fine_lanes=MCTuplesAxisGapPlacement(gaps, counts).offset_fine_lanes,
            )


# ==================================================================================================
#  MCTuplesAxisGaps
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesAxisGaps:
    """`MCTuplesAxisGaps` describes the gaps that the size below leaves on 1 axis and allocates new tuples to them.

    It holds every gap, including those that end up without new tuples, and exists only inside
    `MCTuplesAxisGapAllocation.of`, which keeps the result.

    Every attribute except `lowest_value`, `highest_value`, `n_required` and `required_sum` is an array with 1 entry
    per gap, in ascending order, so that each step of an allocation scores every gap at once.

    Attributes:
        first_lanes: The first free fine lane of each gap, ascending.
        n_free_lanes: The number of free fine lanes of each gap, the most new tuples it can hold.
        is_left_edge: Whether each gap starts at the left edge of the axis, at 0.
        is_right_edge: Whether each gap ends at the right edge of the axis, at 1.
        lows: The lower bound of each gap on the axis: the value of the tuple below it, or 0 for the left edge gap.
        highs: The upper bound of each gap on the axis: the value of the tuple above it, or 1 for the right edge gap.
        lowest_value: The lowest value of the size below on this axis.
        highest_value: The highest value of the size below on this axis.
        n_required: The number of tuples of the size below.
        required_sum: The sum of their values on this axis.
    """

    first_lanes: np.ndarray
    n_free_lanes: np.ndarray
    is_left_edge: np.ndarray
    is_right_edge: np.ndarray
    lows: np.ndarray
    highs: np.ndarray
    lowest_value: float
    highest_value: float
    n_required: int
    required_sum: float

    @property
    def left_edge_gap(self) -> int | None:
        """Return the index of the left edge gap, or None when the lowest fine lane is occupied."""
        return 0 if self.is_left_edge[0] else None

    @property
    def right_edge_gap(self) -> int | None:
        """Return the index of the right edge gap, or None when the highest fine lane is occupied."""
        return self.is_right_edge.size - 1 if self.is_right_edge[-1] else None

    @property
    def edge_gaps(self) -> np.ndarray:
        """Return the indices of the edge gaps, ascending: 0, 1 or 2 of them."""
        return np.flatnonzero(self.is_left_edge | self.is_right_edge)

    # --------------------------------------------------------------------------
    #  Allocations
    # --------------------------------------------------------------------------
    def greedy_counts(self, n_new: int) -> np.ndarray:
        """Return the greedy allocation of `n_new` new tuples: each to the gap that keeps the widest spacing after it.

        A gap takes at most 1 new tuple per free fine lane.
        """
        counts = np.zeros(self.n_free_lanes.size, dtype=np.int64)
        for _ in range(n_new):
            spacing_after_addition = np.where(
                counts >= self.n_free_lanes, -np.inf, MCTuplesAxisGapPlacement(self, counts).spacings_after_adding_1()
            )
            counts[np.argmax(spacing_after_addition)] += 1
        return counts

    def mean_aware_counts(self, greedy_counts: np.ndarray) -> np.ndarray:
        """Return the allocation with a locally largest corrected smallest spacing, reached by moving tuples.

        The corrected smallest spacing is `MCTuplesAxisGapPlacement.corrected_min_spacing`. The search repeatedly moves
        1 new tuple from 1 gap to another, taking the move that raises the corrected smallest spacing most, and stops
        once no move raises it.

        Every move raises the corrected smallest spacing strictly, and there are finitely many allocations, so the
        search ends.

        A gap takes at most 1 new tuple per free fine lane.
        """
        placement = MCTuplesAxisGapPlacement(self, greedy_counts.copy())
        corrected_min_spacing = placement.corrected_min_spacing
        while True:
            corrected_min_spacing_after_each_move = placement.corrected_min_spacing_after_each_move()
            source, destination = np.unravel_index(
                np.argmax(corrected_min_spacing_after_each_move), corrected_min_spacing_after_each_move.shape
            )
            # The chosen move's estimate is recomputed from its allocation. `corrected_min_spacing_after_each_move`
            # builds each estimate from differences of predicted sums, and their rounding could make each of 2
            # allocations with the same estimate look better than the other, so the search would cycle between them.
            #
            # When no move is valid, every entry is -inf, and so is the chosen one, which ends the search.
            if corrected_min_spacing_after_each_move[source, destination] > -np.inf:
                placement_after_move = placement.after_move(int(source), int(destination))
                corrected_min_spacing_after_move = placement_after_move.corrected_min_spacing
            else:
                corrected_min_spacing_after_move = -np.inf
            if corrected_min_spacing_after_move > corrected_min_spacing:
                placement, corrected_min_spacing = placement_after_move, corrected_min_spacing_after_move
            else:
                return placement.counts

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
        return cls(
            first_lanes=lane_below + 1,
            n_free_lanes=n_free,
            is_left_edge=is_left_edge,
            is_right_edge=is_right_edge,
            lows=np.where(is_left_edge, 0.0, value_of_fine_lane[np.maximum(lane_below, 0)]),
            highs=np.where(is_right_edge, 1.0, value_of_fine_lane[np.minimum(lane_above, N_FINE_LANES - 1)]),
            lowest_value=float(required_values.min()),
            highest_value=float(required_values.max()),
            n_required=required_values.size,
            required_sum=float(required_values.sum()),
        )
