"""`GapAllocation` decides how many of a size's new tuples go into each gap that the size below leaves on each axis.

On each axis, every tuple of the size below occupies 1 fine lane. A gap is a maximal run of free fine lanes: between 2
occupied fine lanes, or between an occupied fine lane and an edge of the axis (`AxisGaps`).

The size's max-div solve puts exactly the allocated number of new tuples into each gap, and spreads them about evenly
inside it. So the allocation sets where the size's mean lies, and with it how far the mean correction has to move the
new tuples.

The allocation comes in 2 stages:

1. **greedy:** the new tuples go to the gaps 1 at a time, each to the gap that has the widest spacing after it takes
   the tuple; a gap's spacing is the distance between its neighboring values once its new tuples are spread evenly
   over it;
2. **mean-aware:** starting from the greedy allocation, a local search moves new tuples between gaps until the
   predicted mean is closest to 0.5, while every gap's spacing stays at least (1 - `epsilon`) times the greedy
   allocation's smallest spacing (`AxisGaps.mean_aware_counts`).
"""

from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES, fine_lanes_of

# The mean that every size's u values and v values have once the construction has corrected them.
TARGET_MEAN = 0.5


# ==================================================================================================
#  GapAllocation
# ==================================================================================================
@dataclass(frozen=True)
class GapAllocation:
    """`GapAllocation` holds, for 1 size, the allocation of its new tuples to the gaps along u and along v.

    Attributes:
        u: The allocation along u.
        v: The allocation along v.
    """

    u: "AxisGapAllocation"
    v: "AxisGapAllocation"

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, required_tuple_array: np.ndarray, n_new: int, epsilon: float) -> "GapAllocation":
        """Return the mean-aware allocation of `n_new` new tuples along u and along v of `required_tuple_array`."""
        return cls(
            u=AxisGapAllocation.of(required_tuple_array[:, 0], n_new, epsilon),
            v=AxisGapAllocation.of(required_tuple_array[:, 1], n_new, epsilon),
        )


# ==================================================================================================
#  AxisGapAllocation
# ==================================================================================================
@dataclass(frozen=True)
class AxisGapAllocation:
    """`AxisGapAllocation` holds the allocation chosen for 1 axis of 1 size, in the form that the solve uses.

    `AxisGaps` describes every gap and computes the allocation; `AxisGapAllocation` keeps only the gaps that get new
    tuples, how many each gets, and the predicted offsets for the progress report.

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
    def of(cls, required_values: np.ndarray, n_new: int, epsilon: float) -> "AxisGapAllocation":
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
            gaps = AxisGaps.of(required_values)
            greedy_counts = gaps.greedy_counts(n_new)
            counts = gaps.mean_aware_counts(greedy_counts, epsilon)
            is_used = counts > 0
            return cls(
                gap_of_fine_lane=gaps.gap_of_fine_lane(is_used),
                counts=counts[is_used],
                greedy_offset_fine_lanes=gaps.predicted_offset_fine_lanes(greedy_counts),
                mean_aware_offset_fine_lanes=gaps.predicted_offset_fine_lanes(counts),
            )


# ==================================================================================================
#  AxisGaps
# ==================================================================================================
@dataclass(frozen=True)
class AxisGaps:
    """`AxisGaps` describes the gaps that the size below leaves on 1 axis, and computes their allocation of new tuples.

    It holds every gap, including those that end up without new tuples, and exists only inside `AxisGapAllocation.of`,
    which keeps the result.

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

    def mean_aware_counts(self, greedy_counts: np.ndarray, epsilon: float) -> np.ndarray:
        """Return the allocation that brings the predicted mean closest to 0.5, starting from `greedy_counts`.

        The greedy allocation's smallest spacing is the largest achievable. Each gap may hold new tuples up to the
        largest count that keeps its spacing at least (1 - `epsilon`) times the greedy smallest spacing, and at most
        its number of free fine lanes.

        The search then repeatedly moves 1 new tuple from 1 gap to another, taking the move that brings the predicted
        sum of new values (`predicted_sums`) closest to the sum that puts the size's mean at 0.5, and stops once no
        move brings it closer.
        """
        min_allowed_spacing = (1 - epsilon) * self.spacings(greedy_counts).min()
        max_counts = greedy_counts.copy()
        while True:
            can_grow = (max_counts < self.n_free_lanes) & (self.spacings(max_counts + 1) >= min_allowed_spacing)
            if not can_grow.any():
                break
            max_counts[can_grow] += 1

        n_new = int(greedy_counts.sum())
        target_sum = TARGET_MEAN * (self.n_required + n_new) - self.required_sum
        counts = greedy_counts.copy()
        # Every move brings the excess strictly closer to 0, and the allocations are finite, so the search ends.
        while True:
            sums = self.predicted_sums(counts)
            excess = sums.sum() - target_sum
            removal = sums - self.predicted_sums(counts - 1)
            addition = self.predicted_sums(counts + 1) - sums
            is_valid = (counts >= 1)[:, None] & (counts < max_counts)[None, :]
            np.fill_diagonal(is_valid, False)
            excess_after = np.where(is_valid, np.abs(excess - removal[:, None] + addition[None, :]), np.inf)
            source, destination = np.unravel_index(np.argmin(excess_after), excess_after.shape)
            if excess_after[source, destination] < abs(excess):
                counts[source] -= 1
                counts[destination] += 1
            else:
                break
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
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, required_values: np.ndarray) -> "AxisGaps":
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
