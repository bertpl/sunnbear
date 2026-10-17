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

The first correction of the smallest size rotates each axis instead of the mean correction
(`MCTuplesValueCorrection.first_of`): that size has no size below to keep in place, and a rotation keeps every cyclic
distance, where the mean correction shrinks the largest spacings. An axis on which the rotation would put 2 tuples into
1 fine lane gets the mean correction.

The rules are written for a mean above 0.5, where the new tuples move left, over the size's values u_0 < u_1 < … in
ascending order, with w the width of a fine lane:

- each new tuple i gets a reference r_i and a spacing s_i = u_i - r_i to that reference, both fixed from the values
  before the correction:
  - r_i is 0 when u_i is the lowest value;
  - r_i is the right edge of u_{i-1}'s fine lane when u_{i-1} is a tuple of the size below;
  - r_i is u_{i-1} when u_{i-1} is a new tuple, and then r_i moves when u_{i-1} moves;
- a cap D bounds a new tuple's spacing to its reference, by a rule that depends on the tuple's left neighbor
  (u_{i-1}, or the edge for the lowest value):
  - when the left neighbor is the edge or a tuple of the size below, u'_i = r_i + min(s_i, D);
  - when the left neighbor is a new tuple and s_i ≤ w, u_i stays until u'_{i-1} + w falls below it:
    u'_i = min(u_i, u'_{i-1} + w);
  - when the left neighbor is a new tuple and s_i > w, u_i follows its left neighbor and keeps its spacing, capped
    at w + D: u'_i = u'_{i-1} + min(s_i, w + D).

So the largest spacings shrink first and the smallest keep their value. Every u'_i rises with D without jumps, and a
bisection over D finds the cap at which the mean is exactly 0.5.

The rules measure the lowest value's spacing from the edge of the axis, at 0. max-div measures distances cyclically,
and the lowest value's spacing from 0 is never more than its cyclic spacing from the highest value, its neighbor across
0 and 1, so the mean correction never shrinks that cyclic spacing below the cap D.

No fine lane ever holds 2 tuples, at any D:

- a new tuple whose left neighbor is a tuple of the size below stays above that tuple's fine lane;
- 2 new neighbors end at least w apart or keep their fine lanes;
- the order of the values never changes.

A mean below 0.5 mirrors every rule.
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

FINE_LANE_WIDTH = 1 / N_FINE_LANES

# The bisection's search range for the cap D. The lower bound keeps every moved tuple at least 1e-6 fine
# lanes from the edge of its fine lane, so that a right shift, computed on the negated axis, never puts a tuple on the
# lower edge of its neighbor's fine lane, which belongs to that neighbor. At the upper bound no spacing reaches the cap,
# so nothing moves.
CAP_RANGE = (1e-6 * FINE_LANE_WIDTH, 1.0)

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
            MCTuplesConstructionError: If a fine lane holds 2 tuples after the correction (the correction's rules
                prevent that unless the size already had such a fine lane), or if the nudge finds no value with at least
                `MIN_N_BITS` bits inside a value's fine lane.
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

        The first `n_required` tuples are the size below. The smallest size, with `n_required` 0, gets each axis
        rotated to a mean of 0.5, then nudged (`MCTuplesAxisValueCorrection.of_smallest_size`); an axis on which every
        rotation to a mean of 0.5 puts 2 tuples in 1 fine lane gets the mean correction instead. Every other size gets
        the correction of `of`.

        Raises:
            MCTuplesConstructionError: If the nudge finds no value with at least `MIN_N_BITS` bits inside a value's fine
                lane, or, for every size but the smallest, if a fine lane holds 2 tuples after the correction, as `of`
                raises it.
        """
        if n_required == 0:
            u = MCTuplesAxisValueCorrection.of_smallest_size(tuple_array[:, 0])
            v = MCTuplesAxisValueCorrection.of_smallest_size(tuple_array[:, 1])
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
        immovable_values: np.ndarray, movable_values: np.ndarray, is_shift_left: bool
    ) -> Callable[[float], np.ndarray]:
        """Return the map from the cap D to the moved values of `movable_values`; `immovable_values` stay in place.

        The rules are written for a left shift. A right shift negates the axis, which is exact in floating point, so
        that the left neighbor, the left edge and the right edge of a fine lane become the right neighbor, the right
        edge and the left edge; the right shift then applies the left-shift rules and negates the result back.
        """
        sign = 1.0 if is_shift_left else -1.0
        values = sign * np.concatenate([immovable_values, movable_values])
        order = np.argsort(values)
        sorted_values = values[order].tolist()
        is_movable = (order >= immovable_values.size).tolist()
        left_edge = 0.0 if is_shift_left else -1.0

        def moved_values(cap: float) -> np.ndarray:
            moved = list(sorted_values)
            for i, value in enumerate(sorted_values):
                if not is_movable[i]:
                    continue
                if i == 0:
                    moved[i] = min(value, left_edge + cap)
                elif not is_movable[i - 1]:
                    # The reference is the right edge of the fine lane that holds the left neighbor, an immovable tuple.
                    lane_right_edge = (math.floor(sorted_values[i - 1] * N_FINE_LANES) + 1) * FINE_LANE_WIDTH
                    moved[i] = min(value, lane_right_edge + cap)
                elif value - sorted_values[i - 1] <= FINE_LANE_WIDTH:
                    # Stay, until the left neighbor has moved so far that the tuple has to follow it at a distance of
                    # 1 fine lane.
                    moved[i] = min(value, moved[i - 1] + FINE_LANE_WIDTH)
                else:
                    # Follow the left neighbor and keep the spacing, capped at 1 fine lane plus D; the moved value is
                    # computed from the neighbor's move, so that a tuple whose neighbor stays keeps its value exactly.
                    moved[i] = min(value - (sorted_values[i - 1] - moved[i - 1]), moved[i - 1] + FINE_LANE_WIDTH + cap)
            unsorted = np.empty(len(moved))
            unsorted[order] = moved
            return sign * unsorted[immovable_values.size :]

        return moved_values

    @staticmethod
    def _offset_fine_lanes(movable_values: np.ndarray, target_mean_of_movable: float, size: int) -> float:
        """Return the offset of the size's mean from 0.5, in fine lanes, with these movable values.

        The size's mean is 0.5 exactly when the movable values' mean is `target_mean_of_movable`, so the size's offset
        is the movable values' offset scaled by their share of the size.
        """
        return float((movable_values.mean() - target_mean_of_movable) * movable_values.size / size * N_FINE_LANES)

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
        target_mean_of_movable = (TARGET_MEAN * size - required_values.sum()) / new_values.size
        is_shift_left = bool(new_values.mean() > target_mean_of_movable)
        moved_values_of_cap = cls._moved_values_of_cap(required_values, new_values, is_shift_left)
        cap = cls._solve_cap(moved_values_of_cap, target_mean_of_movable)
        mean_corrected_new_values = moved_values_of_cap(cap)
        corrected_new_values = cls._nudged_values(mean_corrected_new_values)
        return cls(
            cap=cap,
            rotation_shift=None,
            corrected_new_values=corrected_new_values,
            offset_before_fine_lanes=cls._offset_fine_lanes(new_values, target_mean_of_movable, size),
            offset_after_fine_lanes=cls._offset_fine_lanes(corrected_new_values, target_mean_of_movable, size),
            max_move_fine_lanes=float(np.abs(corrected_new_values - new_values).max() * N_FINE_LANES),
            n_nudged=int((corrected_new_values != mean_corrected_new_values).sum()),
        )

    @classmethod
    def of_smallest_size(cls, values: np.ndarray) -> "MCTuplesAxisValueCorrection":
        """Return 1 axis of the smallest size, rotated by a shift modulo 1 to a mean of 0.5, then nudged.

        As the shift grows from 0 to 1, the mean of the `k` values rises with slope 1 and drops by `1/k` each time a
        value wraps from 1 to 0, so 1 or more shifts give a mean of 0.5; the rotation takes the one nearest to 0,
        modulo 1.

        A shift can put 2 values that lie less than 1 fine lane apart into 1 fine lane. The shifts to a mean of 0.5
        differ by multiples of `1/k`, which is a whole number of fine lanes, so if 1 of these shifts puts 2 values into
        1 fine lane, every one of them does; the axis then gets the mean correction instead, the one that `of` gives an
        axis with no size below.

        Raises:
            MCTuplesConstructionError: If the nudge finds no value with `MIN_N_BITS` bits inside a value's fine lane.
        """
        k = values.size
        shifts = []
        for n_wrapped in range(k + 1):
            # Between 2 wraps the mean is `values.mean() + shift - n_wrapped / k`; this shift brings the mean to 0.5
            # only if exactly `n_wrapped` values wrap at it, which the check on the mean of the rotated values confirms.
            shift = TARGET_MEAN - values.mean() + n_wrapped / k
            if 0.0 <= shift < 1.0 and abs(((values + shift) % 1.0).mean() - TARGET_MEAN) < 0.5 / k:
                shifts.append(shift if shift <= 0.5 else shift - 1.0)
        for shift in sorted(shifts, key=abs):
            rotated_values = (values + shift) % 1.0
            # The nudge cannot move a value of exactly 0 to a value with `MIN_N_BITS` bits inside its fine lane, so such
            # a shift is skipped.
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
