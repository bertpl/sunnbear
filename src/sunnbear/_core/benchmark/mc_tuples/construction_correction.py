"""`MeanCorrection` moves a size's new tuples after its max-div solve, so that its mean u and mean v are exactly 0.5.

The tuples of the size below, the old tuples, stay where they are; per axis, only the new tuples move, toward the side
that the mean needs (`AxisMeanCorrection`). The rules are written for a mean above 0.5, where the new tuples move left,
over the size's values u_0 < u_1 < … in ascending order, with w the width of a fine lane:

- each new tuple i gets a reference r_i and a gap g_i = u_i - r_i, both fixed from the values before the correction:
  - r_i is 0 when u_i is the lowest value;
  - r_i is the right edge of u_{i-1}'s fine lane when u_{i-1} is an old tuple;
  - r_i is u_{i-1} when u_{i-1} is a new tuple, and then r_i moves when u_{i-1} moves;
- a cap D bounds the gap that a new tuple keeps to its reference; u_{i-1}, or the edge for the lowest value, is the
  tuple's left neighbor:
  - when the left neighbor is the edge or an old tuple, u'_i = r_i + min(g_i, D);
  - when the left neighbor is a new tuple and g_i ≤ w, u_i stays until u'_{i-1} + w falls below it:
    u'_i = min(u_i, u'_{i-1} + w);
  - when the left neighbor is a new tuple and g_i > w, u_i follows its left neighbor and keeps its gap, capped at
    w + D: u'_i = u'_{i-1} + min(g_i, w + D).

So the largest gaps shrink first and the smallest keep their value. Every u'_i rises with D without jumps, and a
bisection over D finds the cap at which the mean is exactly 0.5.

No fine lane ever holds 2 tuples, at any D: a new tuple whose left neighbor is an old tuple stays above that tuple's
fine lane, 2 new neighbors end at least w apart or keep their fine lanes, and the order of the values never changes.
A mean below 0.5 mirrors every rule.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from .construction_allocation import TARGET_MEAN
from .exceptions import MCTuplesConstructionError
from .sizes import N_FINE_LANES, fine_lanes_of

FINE_LANE_WIDTH = 1 / N_FINE_LANES

# The range that the bisection searches for the cap D. The lower bound keeps every moved tuple at least 1e-6 fine
# lanes from the edge of its fine lane, so that a right shift, computed on the negated axis, never puts a tuple on the
# lower edge of its neighbor's fine lane, which belongs to that neighbor. At the upper bound no gap reaches the cap,
# so nothing moves.
CAP_RANGE = (1e-6 * FINE_LANE_WIDTH, 1.0)

N_BISECTION_STEPS = 200


# ==================================================================================================
#  MeanCorrection
# ==================================================================================================
@dataclass(frozen=True)
class MeanCorrection:
    """`MeanCorrection` holds 1 size after the correction of both axes.

    Attributes:
        u: The u axis after the correction.
        v: The v axis after the correction.
        tuple_array: The size's tuples after the correction, as an `(size, 2)` array: the size below's, then the new
            ones in their original order.
    """

    u: "AxisMeanCorrection"
    v: "AxisMeanCorrection"
    tuple_array: np.ndarray

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def of(cls, tuple_array: np.ndarray, n_required: int) -> "MeanCorrection":
        """Return the size in `tuple_array` after the correction; its first `n_required` tuples are the size below.

        Raises:
            MCTuplesConstructionError: If a fine lane holds 2 tuples after the correction, which the rules rule out
                unless the size already had such a fine lane.
        """
        required, new = tuple_array[:n_required], tuple_array[n_required:]
        u = AxisMeanCorrection.of(required[:, 0], new[:, 0])
        v = AxisMeanCorrection.of(required[:, 1], new[:, 1])
        corrected = np.vstack([required, np.column_stack([u.new_values, v.new_values])])
        for axis, values in (("u", corrected[:, 0]), ("v", corrected[:, 1])):
            if np.bincount(fine_lanes_of(values)).max() > 1:
                raise MCTuplesConstructionError(
                    f"Size {tuple_array.shape[0]}: after the mean correction, a fine {axis}-lane holds 2 tuples."
                )
        return cls(u=u, v=v, tuple_array=corrected)


# ==================================================================================================
#  AxisMeanCorrection
# ==================================================================================================
@dataclass(frozen=True)
class AxisMeanCorrection:
    """`AxisMeanCorrection` holds 1 axis of 1 size after the correction, and what the correction did.

    Attributes:
        cap: The cap D, as a distance on the axis.
        new_values: The new tuples' values after the correction, in their original order.
        offset_before_fine_lanes: The offset of the size's mean from 0.5 before the correction, in fine lanes.
        offset_after_fine_lanes: The same after the correction; apart from rounding, it is 0 unless the correction
            could not reach 0.5.
        max_move_fine_lanes: The largest move of a new tuple, in fine lanes.
    """

    cap: float
    new_values: np.ndarray
    offset_before_fine_lanes: float
    offset_after_fine_lanes: float
    max_move_fine_lanes: float

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _moved_values_of_cap(
        required_values: np.ndarray, new_values: np.ndarray, is_shift_left: bool
    ) -> Callable[[float], np.ndarray]:
        """Return the map from the cap D to the new tuples' moved values.

        The rules are written for a left shift. A right shift negates the axis, which is exact in floating point, so
        that the left neighbor, the left edge and the right edge of a fine lane become the right neighbor, the right
        edge and the left edge; the right shift then applies the left-shift rules and negates the result back.
        """
        sign = 1.0 if is_shift_left else -1.0
        values = sign * np.concatenate([required_values, new_values])
        order = np.argsort(values)
        sorted_values = values[order].tolist()
        is_new = (order >= required_values.size).tolist()
        left_edge = 0.0 if is_shift_left else -1.0

        def moved_values(cap: float) -> np.ndarray:
            moved = list(sorted_values)
            for i, value in enumerate(sorted_values):
                if not is_new[i]:
                    continue
                if i == 0:
                    moved[i] = min(value, left_edge + cap)
                elif not is_new[i - 1]:
                    # The reference is the right edge of the fine lane that holds the old left neighbor.
                    lane_right_edge = (math.floor(sorted_values[i - 1] * N_FINE_LANES) + 1) * FINE_LANE_WIDTH
                    moved[i] = min(value, lane_right_edge + cap)
                elif value - sorted_values[i - 1] <= FINE_LANE_WIDTH:
                    # Stay, until the left neighbor has moved so far that the tuple has to follow it at 1 fine lane.
                    moved[i] = min(value, moved[i - 1] + FINE_LANE_WIDTH)
                else:
                    # Follow the left neighbor and keep the gap, capped at 1 fine lane plus D; the new value is
                    # computed from the neighbor's move, so that a tuple whose neighbor stays keeps its value exactly.
                    moved[i] = min(value - (sorted_values[i - 1] - moved[i - 1]), moved[i - 1] + FINE_LANE_WIDTH + cap)
            unsorted = np.empty(len(moved))
            unsorted[order] = moved
            return sign * unsorted[required_values.size :]

        return moved_values

    @staticmethod
    def _offset_fine_lanes(new_values: np.ndarray, target_mean_of_new: float, size: int) -> float:
        """Return the offset of the size's mean from 0.5, in fine lanes, with these new values.

        The size's mean is 0.5 exactly when the new values' mean is `target_mean_of_new`, so the size's offset is the
        new values' offset scaled by their share of the size.
        """
        return float((new_values.mean() - target_mean_of_new) * new_values.size / size * N_FINE_LANES)

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
    def of(cls, required_values: np.ndarray, new_values: np.ndarray) -> "AxisMeanCorrection":
        """Return 1 axis whose new values moved so that the mean of both arrays' values is 0.5, if possible."""
        size = required_values.size + new_values.size
        target_mean_of_new = (TARGET_MEAN * size - required_values.sum()) / new_values.size
        is_shift_left = bool(new_values.mean() > target_mean_of_new)
        moved_values_of_cap = cls._moved_values_of_cap(required_values, new_values, is_shift_left)
        cap = cls._solve_cap(moved_values_of_cap, target_mean_of_new)
        corrected = moved_values_of_cap(cap)
        return cls(
            cap=cap,
            new_values=corrected,
            offset_before_fine_lanes=cls._offset_fine_lanes(new_values, target_mean_of_new, size),
            offset_after_fine_lanes=cls._offset_fine_lanes(corrected, target_mean_of_new, size),
            max_move_fine_lanes=float(np.abs(corrected - new_values).max() * N_FINE_LANES),
        )
