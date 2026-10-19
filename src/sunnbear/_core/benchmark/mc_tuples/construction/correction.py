"""`MCTuplesValueCorrection` moves a size's new tuples after a max-div solve, in 2 steps that always run together.

1. **The mean correction** moves the new tuples so that the size's u and v means are exactly 0.5.
2. **The nudge** moves each new value with fewer than `MIN_N_BITS` bits of information to the nearest float64 value in
   the same fine lane that has at least `MIN_N_BITS` bits; nearness counts float64 steps
   (`nearest_float_with_min_n_bits`).

   A nudge moves a value by a few float64 steps, so each size's mean stays 0.5 up to rounding, and every tuple keeps
   its fine lane. The values that `MCTuplesPopulation` draws hold at least `MIN_N_BITS` bits, but a value that the mean
   correction moves can hold fewer.

In the mean correction, the tuples of the size below stay where they are; per axis, only the new tuples move, toward
the side that the mean needs (`MCTuplesAxisValueCorrection`).

The rule is written for a mean above 0.5, where the new tuples move left, over the size's values u_0 < u_1 < … in
ascending order.

Each new tuple i has a left neighbor u_{i-1}, a tuple of the size below or a new one. The lowest value's left neighbor
is the highest value minus 1, because on the circle on which max-div measures distances (`distances`), the highest
value is the lowest value's neighbor across 0 and 1.

From the values before the correction, each new tuple i gets:

- a limit l_i, the lowest value that the tuple could take while it stays out of its left neighbor's fine lane: the
  right edge of that fine lane, but never below 0, because a value that crossed 0 would raise the mean, not lower it;
- a halfway point h_i = (u_i + l_i) / 2 between its value and its limit.

A cap D then bounds each new tuple's spacing to its left neighbor's moved value, but no tuple moves past its halfway
point: u'_i = max(h_i, min(u_i, u'_{i-1} + D)). For the lowest value, u'_{i-1} is the highest value minus 1, taken
before the correction moves the highest value, so after the correction the spacing between the 2 can exceed D.

So the largest spacings shrink first and the smallest keep their value. Every u'_i rises with D without jumps, and a
bisection over D finds the cap at which the mean is exactly 0.5.

When the new tuples cannot bring the mean to 0.5 without passing their halfway points, the cap ends at its lower bound,
and `offset_after_fine_lanes` reports the offset that remains.

The halfway point keeps every moved value off its limit, an edge of a fine lane: a value clipped onto its limit would be
a multiple of 1 / N_FINE_LANES and hold fewer than `MIN_N_BITS` bits of information. For a mean below 0.5, where the
new tuples move right, it would also sit on the lower edge of its right neighbor's fine lane, which belongs to that
neighbor.

No fine lane ever holds 2 tuples, at any D: every new tuple stays above its left neighbor's fine lane, and all new
tuples move in the same direction, so the order of the values never changes.

A mean below 0.5 mirrors the rule.

In place of the mean correction, the first correction of the smallest size rotates each axis: it adds the same shift to
every value, modulo 1 (`MCTuplesValueCorrection.first_of`). The smallest size gets a rotation because:

- that size has no size below to keep in place;
- a rotation keeps every distance on the circle on which max-div measures each axis (`distances`), while the mean
  correction shrinks the largest spacings.

An axis on which every rotation to a mean of 0.5 puts 2 values into 1 fine lane or a value on 0 gets the mean correction
(`MCTuplesAxisValueCorrection.of_rotation_or_mean_correction`).
"""

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import (
    MIN_N_BITS,
    N_FINE_LANES,
    TARGET_MEAN,
    fine_lane_edges_of,
    fine_lanes_of,
)
from sunnbear._core.utils.float_bits import nearest_float_with_min_n_bits

from .exceptions import MCTuplesConstructionError

# CAP_RANGE is the bisection's search range for the cap D. At the lower bound every new tuple moves as far as its
# halfway point or its left neighbor allows; at the upper bound no spacing reaches the cap, so nothing moves.
CAP_RANGE = (0.0, 1.0)

N_BISECTION_STEPS = 200


# ==================================================================================================
#  MCTuplesValueCorrection
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesValueCorrection:
    """`MCTuplesValueCorrection` holds 1 size after the correction of both axes.

    Attributes:
        u: The u axis after the correction.
        v: The v axis after the correction.
        tuple_array: The size's tuples after the correction, as an `(size, 2)` array: the size below's, then the new
            ones in their original order.
    """

    u: "MCTuplesAxisValueCorrection"
    v: "MCTuplesAxisValueCorrection"
    tuple_array: np.ndarray

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, tuple_array: np.ndarray, n_required: int) -> "MCTuplesValueCorrection":
        """Return the size in `tuple_array` after the correction; its first `n_required` tuples are the size below.

        Raises:
            MCTuplesConstructionError: If a fine lane holds 2 tuples after the correction (the correction's rule
                prevents that unless the size already had such a fine lane), or if the nudge finds no value with at
                least `MIN_N_BITS` bits inside a value's fine lane.
        """
        required, new = tuple_array[:n_required], tuple_array[n_required:]
        u = MCTuplesAxisValueCorrection.of(required[:, 0], new[:, 0])
        v = MCTuplesAxisValueCorrection.of(required[:, 1], new[:, 1])
        corrected_tuple_array = np.vstack([required, np.column_stack([u.corrected_new_values, v.corrected_new_values])])
        for axis, values in (("u", corrected_tuple_array[:, 0]), ("v", corrected_tuple_array[:, 1])):
            if np.bincount(fine_lanes_of(values)).max() > 1:
                raise MCTuplesConstructionError(
                    f"Size {tuple_array.shape[0]}: after the value correction, a fine {axis}-lane holds 2 tuples."
                )
        return cls(u=u, v=v, tuple_array=corrected_tuple_array)

    @classmethod
    def first_of(cls, tuple_array: np.ndarray, n_required: int) -> "MCTuplesValueCorrection":
        """Return the first value correction of the size whose tuples are `tuple_array`.

        The first `n_required` tuples are the size below. The smallest size, with `n_required` 0, gets each axis rotated
        to a mean of 0.5 and then nudged; an axis on which every such rotation puts 2 values into 1 fine lane or a value
        on 0 gets the mean correction instead (`MCTuplesAxisValueCorrection.of_rotation_or_mean_correction`). Every
        other size gets the correction of `of`.

        Raises:
            MCTuplesConstructionError: If the nudge finds no value with at least `MIN_N_BITS` bits inside a value's fine
                lane, or if `of` finds a fine lane that holds 2 tuples after the correction.
        """
        if n_required == 0:
            u = MCTuplesAxisValueCorrection.of_rotation_or_mean_correction(tuple_array[:, 0])
            v = MCTuplesAxisValueCorrection.of_rotation_or_mean_correction(tuple_array[:, 1])
            return cls(u=u, v=v, tuple_array=np.column_stack([u.corrected_new_values, v.corrected_new_values]))
        else:
            return cls.of(tuple_array, n_required)


# ==================================================================================================
#  MCTuplesAxisValueCorrection
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesAxisValueCorrection:
    """`MCTuplesAxisValueCorrection` holds 1 axis of 1 size after the correction, and what the correction did.

    Attributes:
        cap: The cap D of the mean correction, as a distance on the axis; None for a rotation.
        rotation_shift: The shift of the rotation, as a distance on the axis in (-0.5, 0.5]; None for the mean
            correction.
        corrected_new_values: The new tuples' values after the correction, in their original order.
        offset_before_fine_lanes: The offset of the size's mean from 0.5 before the correction, in fine lanes.
        offset_after_fine_lanes: The same after the correction; apart from rounding, it is 0 unless the correction
            could not reach 0.5.
        max_move_fine_lanes: The largest move of a new tuple, in fine lanes, measured cyclically.
        n_nudged: The number of new values that the nudge moved.
    """

    cap: float | None
    rotation_shift: float | None
    corrected_new_values: np.ndarray
    offset_before_fine_lanes: float
    offset_after_fine_lanes: float
    max_move_fine_lanes: float
    n_nudged: int

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _moved_values_of_cap(
        required_values: np.ndarray, new_values: np.ndarray, is_shift_left: bool
    ) -> Callable[[float], np.ndarray]:
        """Return the map from the cap D to the moved values of `new_values`; `required_values` stay in place.

        The rule is written for a left shift. A right shift negates the axis, which is exact in floating point, so
        that the left neighbor, the left edge and the right edge of a fine lane become the right neighbor, the right
        edge and the left edge; the right shift then applies the left-shift rule and negates the result back.
        """
        sign = 1.0 if is_shift_left else -1.0
        values = sign * np.concatenate([required_values, new_values])
        order = np.argsort(values)
        sorted_values = values[order].tolist()
        is_new = (order >= required_values.size).tolist()
        # axis_left_edge is the left edge of the axis: 0, or -1 on the negated axis of a right shift.
        axis_left_edge = 0.0 if is_shift_left else -1.0

        # Each new value's halfway point is fixed from the values before the correction; the module docstring defines
        # the limit and the lowest value's left neighbor.
        left_neighbors = np.array([sorted_values[-1] - 1.0, *sorted_values[:-1]])
        _, left_neighbor_fine_lane_right_edges = fine_lane_edges_of(fine_lanes_of(left_neighbors))
        halfway_points = [-math.inf] * len(sorted_values)
        for i, value in enumerate(sorted_values):
            if is_new[i]:
                limit = max(float(left_neighbor_fine_lane_right_edges[i]), axis_left_edge)
                halfway_points[i] = 0.5 * (value + limit)

        def moved_values(cap: float) -> np.ndarray:
            moved = list(sorted_values)
            for i, value in enumerate(sorted_values):
                if is_new[i]:
                    # For the lowest value, moved[-1] still holds the highest value from before the correction, because
                    # the loop has not reached it yet, so the cap is measured from that highest value minus 1. The
                    # highest value can only move left, away from the lowest value across 0, so after the correction
                    # the spacing between the 2 can exceed D.
                    moved_left_neighbor = moved[i - 1] if i > 0 else moved[-1] - 1.0
                    moved[i] = max(halfway_points[i], min(value, moved_left_neighbor + cap))
            unsorted = np.empty(len(moved))
            unsorted[order] = moved
            return sign * unsorted[required_values.size :]

        return moved_values

    @staticmethod
    def _offset_fine_lanes(new_values: np.ndarray, target_mean_of_new_values: float, size: int) -> float:
        """Return the offset of the size's mean from 0.5, in fine lanes, with these new values.

        The size's mean is 0.5 exactly when the new values' mean is `target_mean_of_new_values`, so the size's offset
        is the new values' offset scaled by their share of the size.
        """
        return float((new_values.mean() - target_mean_of_new_values) * new_values.size / size * N_FINE_LANES)

    @staticmethod
    def _nudged_values(values: np.ndarray) -> np.ndarray:
        """Return `values`, each moved to the nearest value in its fine lane with at least `MIN_N_BITS` bits.

        Raises:
            MCTuplesConstructionError: If a value's fine lane holds no value with at least `MIN_N_BITS` bits within the
                search range of `nearest_float_with_min_n_bits`.
        """
        nudged = values.copy()
        lows, highs = fine_lane_edges_of(fine_lanes_of(values))
        for i, (value, low, high) in enumerate(zip(values.tolist(), lows.tolist(), highs.tolist(), strict=True)):
            nearest = nearest_float_with_min_n_bits(value, MIN_N_BITS, low, high)
            if nearest is None:
                raise MCTuplesConstructionError(
                    f"No value with at least {MIN_N_BITS} bits lies in the fine lane of {value!r}, within the search "
                    "range of nearest_float_with_min_n_bits."
                )
            nudged[i] = nearest
        return nudged

    @staticmethod
    def _solve_cap(moved_values_of_cap: Callable[[float], np.ndarray], target_mean: float) -> float:
        """Return the cap in `CAP_RANGE` at which the moved values' mean is `target_mean`, or the nearest bound.

        As the cap falls, the mean moves steadily away from its value before the correction, in the direction of the
        shift.
        """
        low, high = CAP_RANGE
        mean_before = moved_values_of_cap(high).mean()
        for _ in range(N_BISECTION_STEPS):
            mid = 0.5 * (low + high)
            if abs(moved_values_of_cap(mid).mean() - mean_before) < abs(target_mean - mean_before):
                high = mid
            else:
                low = mid
        return 0.5 * (low + high)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, required_values: np.ndarray, new_values: np.ndarray) -> "MCTuplesAxisValueCorrection":
        """Return 1 axis whose new values moved so that the mean of both arrays' values is 0.5, if possible.

        The nudge then moves every new value with fewer than `MIN_N_BITS` bits.

        Raises:
            MCTuplesConstructionError: If the nudge finds no value with `MIN_N_BITS` bits inside a value's fine lane.
        """
        size = required_values.size + new_values.size
        target_mean_of_new_values = (TARGET_MEAN * size - required_values.sum()) / new_values.size
        is_shift_left = bool(new_values.mean() > target_mean_of_new_values)
        moved_values_of_cap = cls._moved_values_of_cap(required_values, new_values, is_shift_left)
        cap = cls._solve_cap(moved_values_of_cap, target_mean_of_new_values)
        mean_corrected_new_values = moved_values_of_cap(cap)
        corrected_new_values = cls._nudged_values(mean_corrected_new_values)
        return cls(
            cap=cap,
            rotation_shift=None,
            corrected_new_values=corrected_new_values,
            offset_before_fine_lanes=cls._offset_fine_lanes(new_values, target_mean_of_new_values, size),
            offset_after_fine_lanes=cls._offset_fine_lanes(corrected_new_values, target_mean_of_new_values, size),
            max_move_fine_lanes=float(np.abs(corrected_new_values - new_values).max() * N_FINE_LANES),
            n_nudged=int((corrected_new_values != mean_corrected_new_values).sum()),
        )

    @classmethod
    def of_rotation_or_mean_correction(cls, values: np.ndarray) -> "MCTuplesAxisValueCorrection":
        """Return 1 axis of the smallest size, rotated by a shift modulo 1 to a mean of 0.5, then nudged.

        The rotation takes, among the shifts that bring the mean to 0.5, the one nearest to 0, modulo 1, that puts no 2
        values into 1 fine lane and no value exactly on 0, because the nudge cannot move a value of 0 to a value with
        `MIN_N_BITS` bits.

        When no shift passes both checks, the axis gets the mean correction instead, computed by `of` as for an axis
        with no size below.

        A shift can put 2 values that lie less than 1 fine lane apart into 1 fine lane.

        With `k` the number of values, the shifts to a mean of 0.5 differ by multiples of `1/k`, which is a whole number
        of fine lanes, so if 1 of these shifts puts 2 values into 1 fine lane, every one of them does, and the axis gets
        the mean correction.

        Raises:
            MCTuplesConstructionError: If the nudge finds no value with `MIN_N_BITS` bits inside a value's fine lane.
        """
        k = values.size
        shifts = []
        for n_wrapped in range(k + 1):
            # As the shift grows from 0 to 1, the mean rises with slope 1 and drops by `1/k` each time a value wraps
            # from 1 to 0, so between 2 wraps it is `values.mean() + shift - n_wrapped / k`.
            #
            # This shift brings the mean to 0.5 only if adding it carries exactly `n_wrapped` values past 1, which the
            # check on the mean of the rotated values confirms.
            shift = TARGET_MEAN - values.mean() + n_wrapped / k
            if 0.0 <= shift < 1.0 and abs(((values + shift) % 1.0).mean() - TARGET_MEAN) < 0.5 / k:
                shifts.append(shift if shift <= 0.5 else shift - 1.0)
        for shift in sorted(shifts, key=abs):
            rotated_values = (values + shift) % 1.0
            # The nudge cannot move a value of exactly 0 to a value with `MIN_N_BITS` bits inside its fine lane, so
            # a shift that puts a value on 0 is skipped.
            if np.bincount(fine_lanes_of(rotated_values)).max() == 1 and rotated_values.min() > 0.0:
                corrected_values = cls._nudged_values(rotated_values)
                moves = np.abs(corrected_values - values)
                return cls(
                    cap=None,
                    rotation_shift=shift,
                    corrected_new_values=corrected_values,
                    offset_before_fine_lanes=cls._offset_fine_lanes(values, TARGET_MEAN, k),
                    offset_after_fine_lanes=cls._offset_fine_lanes(corrected_values, TARGET_MEAN, k),
                    max_move_fine_lanes=float(np.minimum(moves, 1.0 - moves).max() * N_FINE_LANES),
                    n_nudged=int((corrected_values != rotated_values).sum()),
                )
        return cls.of(np.zeros(0), values)
