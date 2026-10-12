"""`MCTuplesAxisGapPlacement` predicts where the size's max-div solve puts each gap's new tuples, for 1 allocation.

The prediction is for 1 axis, and for 1 allocation of new tuples to the gaps that the `allocation` module defines.

Each gap spreads its new tuples evenly, and where they lie depends on the kind of gap, with c the gap's number of new
tuples:

- **interior gap:** the c values split the stretch between the values of the 2 neighboring tuples into c + 1 equal
  parts;
- **edge gap:** the outermost value lies on the edge of the axis, at 0 or 1, and the c values split the stretch between
  the edge and the neighboring tuple's value into c equal parts.

The stretch is measured between values, not counted from fine lane indices, because 2 gaps with the same number of free
fine lanes can differ in the length of that stretch by almost 2 fine lanes, depending on where each neighboring tuple's
value lies inside its fine lane.

The size's max-div solve puts an edge gap's outermost new tuple inside the outermost fine lane, not on the edge, so the
placement overstates the span of an edge gap's new tuples by at most 1 fine lane.

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
    @cached_property
    def steps(self) -> np.ndarray:
        """Return the distance between consecutive new values of each gap on the axis; 0 for a gap without any."""
        is_edge = self.gaps.is_left_edge | self.gaps.is_right_edge
        n_parts = np.where(is_edge, self.counts, self.counts + 1)
        steps = (self.gaps.highs - self.gaps.lows) / np.maximum(n_parts, 1)
        return np.where(self.counts > 0, steps, 0.0)

    @cached_property
    def first_values(self) -> np.ndarray:
        """Return the lowest new value of each gap: 0 for the left edge gap, 1 step above its lower bound otherwise."""
        return np.where(self.gaps.is_left_edge, 0.0, self.gaps.lows + self.steps)

    def values(self, gap: int) -> np.ndarray:
        """Return the new values of `gap`, ascending."""
        return self.first_values[gap] + self.steps[gap] * np.arange(max(int(self.counts[gap]), 0))

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
        """Return each gap's spacing, the distance between neighboring values, in fine lanes; inf for an empty gap."""
        return np.where(self.counts > 0, self.steps * N_FINE_LANES, np.inf)

    @cached_property
    def sums(self) -> np.ndarray:
        """Return the sum of each gap's new values."""
        counts = np.maximum(self.counts, 0)
        return counts * self.first_values + self.steps * counts * (counts - 1) / 2

    @property
    def offset_fine_lanes(self) -> float:
        """Return the offset of the size's mean from `TARGET_MEAN`, in fine lanes, with the size below included."""
        size = self.gaps.n_required + int(self.counts.sum())
        mean = (self.gaps.required_sum + self.sums.sum()) / size
        return float((mean - TARGET_MEAN) * N_FINE_LANES)

    @property
    def corrected_min_spacing(self) -> float:
        """Return the estimated smallest spacing, in fine lanes, after the first mean correction moved the new tuples.

        It is a heuristic: it counts each fine lane of offset of the size's mean from `TARGET_MEAN` as 1 fine lane of
        lost spacing, without modeling how the first mean correction moves the new tuples.
        """
        return float(self.spacings.min() - abs(self.offset_fine_lanes))

    def corrected_min_spacing_after_each_move(self) -> np.ndarray:
        """Return the matrix whose entry `[s, d]` is `corrected_min_spacing` after moving 1 tuple from gap `s` to `d`.

        An entry is -inf for a move that is not valid:

        - a move out of a gap without new tuples;
        - a move into a gap without free fine lanes;
        - a move from a gap to itself.
        """
        # A move leaves the size unchanged, and changes the sums of gaps `s` and `d` only.
        size = self.gaps.n_required + int(self.counts.sum())
        excess = self.gaps.required_sum + self.sums.sum() - TARGET_MEAN * size
        removal = self.sums - self._with_1_fewer_per_gap.sums
        addition = self._with_1_more_per_gap.sums - self.sums
        offset_after = np.abs(excess - removal[:, None] + addition[None, :]) / size * N_FINE_LANES
        is_valid = (self.counts >= 1)[:, None] & (self.counts < self.gaps.n_free_lanes)[None, :]
        np.fill_diagonal(is_valid, False)
        return np.where(is_valid, self._min_spacing_after_each_move() - offset_after, -np.inf)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
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

        A move changes the spacings of `s` and `d` only, so the smallest spacing after the move is the smallest of 3
        values: the new spacings of `s` and `d`, and the smallest spacing among the other gaps, which is 1 of the 3
        smallest spacings before the move.
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
