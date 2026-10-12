"""`MCTuplesGapPlacement` holds the values that the gap allocation assumes for 1 allocation of new tuples to gaps.

The gap allocation (`allocation`) scores an allocation by where its new tuples would lie if each gap spread them
evenly. That placement depends on the kind of gap, with c the gap's number of new tuples:

- **interior gap:** the c values split the stretch between the values of the 2 neighboring tuples into c + 1 equal
  parts;
- **edge gap:** the outermost value lies on the edge of the axis, at 0 or 1, and the c values split the stretch between
  the edge and the neighboring tuple's value into c equal parts.

The stretch is measured between values, not counted from fine lane indices, because 2 gaps with the same number of free
fine lanes can differ in width by almost 2 fine lanes, depending on where their neighbors lie inside their fine lanes.
An edge gap's outermost new tuple actually lies inside the outermost fine lane, so the placement overstates the span of
an edge gap's new tuples by at most 1 fine lane.

Each gap's placement is a first value and a step, and every prediction derives from them: the values, the spacings,
their sum, and the size's mean.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import N_FINE_LANES, TARGET_MEAN

if TYPE_CHECKING:
    from .allocation import MCTuplesAxisGaps


# ==================================================================================================
#  MCTuplesGapPlacement
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesGapPlacement:
    """`MCTuplesGapPlacement` places each gap's new tuples evenly, for 1 allocation of new tuples to the gaps.

    Every array has 1 entry per gap of `gaps`. A gap without new tuples has no values: its spacing is inf and its sum
    is 0. A negative count, which the mean-aware search forms for a move out of an empty gap, counts as 0.

    Attributes:
        gaps: The gaps that the size below leaves on 1 axis.
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
        """Return the offset of the size's mean from 0.5, in fine lanes, with the size below's tuples included."""
        size = self.gaps.n_required + int(self.counts.sum())
        mean = (self.gaps.required_sum + self.sums.sum()) / size
        return float((mean - TARGET_MEAN) * N_FINE_LANES)

    @property
    def corrected_min_spacing(self) -> float:
        """Return the estimated smallest spacing, in fine lanes, once the mean correction has moved the new tuples.

        The estimate is the smallest spacing minus the absolute offset of the size's mean from 0.5. It is a heuristic:
        it counts each fine lane of offset as 1 fine lane of lost spacing, without modeling how the mean correction
        moves the new tuples.
        """
        return float(self.spacings.min() - abs(self.offset_fine_lanes))
