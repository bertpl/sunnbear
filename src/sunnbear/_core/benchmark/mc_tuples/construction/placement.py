"""`MCTuplesAxisGapPlacement` predicts where the size's max-div solve puts each gap's new tuples, for 1 allocation.

The prediction is for 1 axis, and for 1 allocation of new tuples to the gaps that the `allocation` module defines.

max-div measures distances cyclically (`distances`): each axis is a circle on which 0 and 1 meet. The stretch from the
highest value of the size below, across 1 and 0, to its lowest value is then 1 gap, the wrap-around gap.

Its 2 parts keep a count of new tuples each, because the side on which a new tuple lies decides whether it raises or
lowers the size's mean:

- the left edge gap runs from 0 to the lowest value;
- the right edge gap runs from the highest value to 1.

Each gap spreads its new tuples evenly, with c the gap's number of new tuples:

- **interior gap:** the c values split the stretch between the values of the 2 neighboring tuples into c + 1 equal
  parts;
- **edge gaps:** the c_left + c_right values of the 2 edge gaps share the wrap-around gap:
  - when an even split into c_left + c_right + 1 equal parts puts exactly c_right of the values between the highest
    value of the size below and 1, the values take that split;
  - otherwise 1 side holds too many values for the even split, which would carry some of them across the point where 0
    and 1 meet: that side spreads its values up to that point, with its outermost value on it, and the other side
    splits its own part evenly (`_edge_gap_first_values_and_steps`).

When 1 side holds too many values, the size's max-div solve puts that side's outermost value inside the outermost fine
lane, not on the point where 0 and 1 meet, so the placement overstates the span of that side's new values by at most 1
fine lane.

Each edge gap that holds new tuples reports the spacing of the whole wrap-around gap, the smaller of the 2 sides'
distances between neighboring values, so that adding a tuple to 1 side shows in the spacing of both.

The stretch is measured between values, not counted from fine lane indices, because 2 gaps with the same number of free
fine lanes can differ in the length of that stretch by almost 2 fine lanes, depending on where each neighboring tuple's
value lies inside its fine lane.

Each gap's placement is a first value and a step, and `values`, `spacings` and `sums` all derive from these 2 numbers,
so the spacings and sums always match the values that `values` returns.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES, TARGET_MEAN

if TYPE_CHECKING:
    from .allocation import MCTuplesAxisGaps


# ==================================================================================================
#  MCTuplesAxisGapPlacement
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesAxisGapPlacement:
    """`MCTuplesAxisGapPlacement` places each gap's new tuples evenly, for 1 allocation of new tuples to the gaps.

    Every property that returns an array has 1 entry per gap of `gaps`. A gap without new tuples has no values: its
    spacing is inf and its sum is 0. A negative count, which `_with_1_fewer_per_gap` forms for a gap without new tuples,
    counts as 0 in the values, spacings and sums.

    Attributes:
        gaps: The gaps of free fine lanes on 1 axis, around the size below's tuples.
        counts: The number of new tuples of each gap.
    """

    gaps: "MCTuplesAxisGaps"
    counts: np.ndarray

    # --------------------------------------------------------------------------
    #  Placement
    # --------------------------------------------------------------------------
    def values(self, gap: int) -> np.ndarray:
        """Return the new values of `gap`, ascending."""
        first_values, steps = self._first_values_and_steps
        return first_values[gap] + steps[gap] * np.arange(max(int(self.counts[gap]), 0))

    def after_move(self, source: int, destination: int) -> "MCTuplesAxisGapPlacement":
        """Return the placement after moving 1 new tuple from gap `source` to gap `destination`."""
        counts = self.counts.copy()
        counts[source] -= 1
        counts[destination] += 1
        return MCTuplesAxisGapPlacement(self.gaps, counts)

    # --------------------------------------------------------------------------
    #  Predictions
    # --------------------------------------------------------------------------
    @cached_property
    def spacings(self) -> np.ndarray:
        """Return each gap's spacing, the distance between neighboring values, in fine lanes; inf for an empty gap.

        Each edge gap with new tuples reports the spacing of the wrap-around gap, the smaller of the 2 edge gaps' steps.
        """
        has_values = self.counts > 0
        spacings = np.where(has_values, self._first_values_and_steps[1] * N_FINE_LANES, np.inf)
        edge_gaps = np.flatnonzero(self.gaps.is_left_edge | self.gaps.is_right_edge)
        if edge_gaps.size > 0:
            spacings[edge_gaps] = np.where(has_values[edge_gaps], spacings[edge_gaps].min(), np.inf)
        return spacings

    def spacings_after_each_addition(self) -> np.ndarray:
        """Return each gap's spacing, in fine lanes, after that gap alone takes 1 more new tuple.

        Adding a tuple to 1 edge gap changes the placement of both, so each edge gap's entry comes from a placement with
        1 more tuple in that edge gap only; an interior gap's spacing depends on its own count only, so every interior
        gap's entry comes from 1 placement with 1 more tuple in every gap.
        """
        spacings = self._with_1_more_per_gap.spacings.copy()
        for gap in np.flatnonzero(self.gaps.is_left_edge | self.gaps.is_right_edge):
            counts = self.counts.copy()
            counts[gap] += 1
            spacings[gap] = MCTuplesAxisGapPlacement(self.gaps, counts).spacings[gap]
        return spacings

    @cached_property
    def sums(self) -> np.ndarray:
        """Return the sum of each gap's new values."""
        counts = np.maximum(self.counts, 0)
        first_values, steps = self._first_values_and_steps
        return counts * first_values + steps * counts * (counts - 1) / 2

    @property
    def offset_fine_lanes(self) -> float:
        """Return the offset of the size's mean from `TARGET_MEAN`, in fine lanes, with the size below included."""
        size = self.gaps.n_required + int(self.counts.sum())
        mean = (self.gaps.required_sum + self.sums.sum()) / size
        return float((mean - TARGET_MEAN) * N_FINE_LANES)

    @property
    def offset_weight(self) -> float:
        """Return the drop in the smallest spacing, in fine lanes, per fine lane of the size's mean offset.

        Only the new tuples move in the first value correction, so to remove an offset of the size's mean they move on
        average by that offset times the size's total number of tuples divided by its number of new tuples.

        In an evenly spread size nearly all new tuples move, so the smallest spacing drops by about the average move of
        the new tuples.
        """
        n_new = int(self.counts.sum())
        return (self.gaps.n_required + n_new) / n_new

    @property
    def corrected_min_spacing(self) -> float:
        """Return the estimated smallest spacing, in fine lanes, once the first value correction has run.

        It is a heuristic: for every fine lane of offset of the size's mean from `TARGET_MEAN`, it subtracts
        `offset_weight` fine lanes, without modeling how the first value correction moves each new tuple.
        """
        return float(self.spacings.min() - self.offset_weight * abs(self.offset_fine_lanes))

    def corrected_min_spacing_after_each_move(self) -> np.ndarray:
        """Return the matrix whose entry `[s, d]` is `corrected_min_spacing` after moving 1 tuple from gap `s` to `d`.

        An entry is -inf for a move that is not valid:

        - a move out of a gap without new tuples;
        - a move into a gap without free fine lanes;
        - a move from a gap to itself.

        A move between interior gaps changes the spacings and sums of gaps `s` and `d` only, so those entries are
        computed for all moves at once. A move into or out of an edge gap also changes the other edge gap's placement,
        so each such entry is computed from the placement after that move.
        """
        # A move leaves the size unchanged, and changes the sums of gaps `s` and `d` only.
        size = self.gaps.n_required + int(self.counts.sum())
        excess = self.gaps.required_sum + self.sums.sum() - TARGET_MEAN * size
        removal = self.sums - self._with_1_fewer_per_gap.sums
        addition = self._with_1_more_per_gap.sums - self.sums
        offset_after = np.abs(excess - removal[:, None] + addition[None, :]) / size * N_FINE_LANES
        is_valid = (self.counts >= 1)[:, None] & (self.counts < self.gaps.n_free_lanes)[None, :]
        np.fill_diagonal(is_valid, False)
        # Moving 1 tuple between gaps keeps the number of new tuples, so `offset_weight` is the same for every entry.
        corrected_min_spacings = np.where(
            is_valid, self._min_spacing_after_each_move() - self.offset_weight * offset_after, -np.inf
        )
        for edge_gap in np.flatnonzero(self.gaps.is_left_edge | self.gaps.is_right_edge).tolist():
            moves = [(edge_gap, destination) for destination in np.flatnonzero(is_valid[edge_gap]).tolist()]
            moves += [(source, edge_gap) for source in np.flatnonzero(is_valid[:, edge_gap]).tolist()]
            for source, destination in moves:
                corrected_min_spacings[source, destination] = self.after_move(source, destination).corrected_min_spacing
        return corrected_min_spacings

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @cached_property
    def _first_values_and_steps(self) -> tuple[np.ndarray, np.ndarray]:
        """Return the first value and the step of each gap; the step is 0 for a gap without new tuples.

        A count of -1, which `_with_1_fewer_per_gap` gives an empty gap, counts as 0.
        """
        counts = np.maximum(self.counts, 0)
        steps = (self.gaps.highs - self.gaps.lows) / (counts + 1)
        first_values = self.gaps.lows + steps
        left_edge_gap = 0 if self.gaps.is_left_edge[0] else None
        right_edge_gap = self.gaps.is_right_edge.size - 1 if self.gaps.is_right_edge[-1] else None
        if left_edge_gap is not None or right_edge_gap is not None:
            n_left = int(counts[left_edge_gap]) if left_edge_gap is not None else 0
            n_right = int(counts[right_edge_gap]) if right_edge_gap is not None else 0
            left_first, left_step, right_first, right_step = self._edge_gap_first_values_and_steps(
                self.gaps.lowest_required_value, self.gaps.highest_required_value, n_left, n_right
            )
            if left_edge_gap is not None:
                first_values[left_edge_gap], steps[left_edge_gap] = left_first, left_step
            if right_edge_gap is not None:
                first_values[right_edge_gap], steps[right_edge_gap] = right_first, right_step
        return first_values, np.where(counts > 0, steps, 0.0)

    @staticmethod
    def _edge_gap_first_values_and_steps(
        lowest_required_value: float, highest_required_value: float, n_left: int, n_right: int
    ) -> tuple[float, float, float, float]:
        """Return the first value and the step of the left edge gap, then those of the right edge gap.

        The left edge gap holds `n_left` new values between 0 and `lowest_required_value`, the right edge gap `n_right`
        between `highest_required_value` and 1; the module docstring describes the cases. A side without values still
        gets a first value and a step, which no caller reads, because a gap without new tuples has no values.
        """
        left_width, right_width = lowest_required_value, 1.0 - highest_required_value
        even_step = (left_width + right_width) / (n_left + n_right + 1)
        if n_left > 0:
            left_step_reaching_0 = left_width / n_left
        else:
            left_step_reaching_0 = np.inf
        if n_right > 0:
            right_step_reaching_1 = right_width / n_right
        else:
            right_step_reaching_1 = np.inf
        if even_step <= min(left_step_reaching_0, right_step_reaching_1):
            # The values split the wrap-around gap evenly, from the highest value across 1 and 0 to the lowest value.
            left_first, left_step = highest_required_value + (n_right + 1) * even_step - 1.0, even_step
            right_first, right_step = highest_required_value + even_step, even_step
        elif right_step_reaching_1 < left_step_reaching_0:
            # The right side holds too many values: its highest value lies on 1.
            left_step = left_width / (n_left + 1)
            left_first = left_step
            right_first, right_step = highest_required_value + right_step_reaching_1, right_step_reaching_1
        else:
            # The left side holds too many values: its lowest value lies on 0.
            left_first, left_step = 0.0, left_step_reaching_0
            right_step = right_width / (n_right + 1)
            right_first = highest_required_value + right_step
        return left_first, left_step, right_first, right_step

    @cached_property
    def _with_1_fewer_per_gap(self) -> "MCTuplesAxisGapPlacement":
        """Return the placement with 1 new tuple fewer in every gap; an empty gap's count becomes -1."""
        return MCTuplesAxisGapPlacement(self.gaps, self.counts - 1)

    @cached_property
    def _with_1_more_per_gap(self) -> "MCTuplesAxisGapPlacement":
        """Return the placement with 1 new tuple more in every gap."""
        return MCTuplesAxisGapPlacement(self.gaps, self.counts + 1)

    def _min_spacing_after_each_move(self) -> np.ndarray:
        """Return the matrix whose entry `[s, d]` is the smallest spacing after moving 1 tuple from gap `s` to gap `d`.

        A move between interior gaps changes the spacings of `s` and `d` only, so the smallest spacing after the move is
        the smallest of 3 values: the new spacings of `s` and `d`, and the smallest spacing among the other gaps, which
        is 1 of the 3 smallest spacings before the move. The entries of moves into or out of an edge gap leave out the
        change to the other edge gap, so they are wrong; `corrected_min_spacing_after_each_move` replaces them.
        """
        spacings = self.spacings
        n_gaps = spacings.size
        min_spacing_gaps = np.argsort(spacings)[:3]
        gap_indices = np.arange(n_gaps)
        # Each entry starts at the 3rd smallest spacing. The 2nd smallest spacing, then the smallest, replaces it in
        # every entry whose move leaves the gap of that spacing untouched.
        if n_gaps >= 3:
            min_spacing_of_others = np.full((n_gaps, n_gaps), spacings[min_spacing_gaps[2]])
        else:
            min_spacing_of_others = np.full((n_gaps, n_gaps), np.inf)
        for rank in reversed(range(min(2, n_gaps))):
            gap = min_spacing_gaps[rank]
            is_other = (gap_indices[:, None] != gap) & (gap_indices[None, :] != gap)
            min_spacing_of_others = np.where(is_other, spacings[gap], min_spacing_of_others)
        return np.minimum(
            min_spacing_of_others,
            np.minimum(self._with_1_fewer_per_gap.spacings[:, None], self._with_1_more_per_gap.spacings[None, :]),
        )
