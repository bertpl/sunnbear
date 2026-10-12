"""`MCTuplesGapPlacement` spreads each gap's new tuples evenly, and derives its spacings, sums and mean from those
values."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES
from sunnbear._core.benchmark.mc_tuples.construction.allocation import MCTuplesAxisGaps
from sunnbear._core.benchmark.mc_tuples.construction.placement import MCTuplesGapPlacement

# The tuples of the size below lie in fine lanes 3, 10 and 11, which leaves a left edge gap below 3.5, an interior gap
# between 3.5 and 10.25, and a right edge gap above 11.5, in fine lanes.
_VALUES = np.array([3.5, 10.25, 11.5]) / N_FINE_LANES


@pytest.mark.parametrize("count", [1, 2, 3])
def test_values_follow_an_even_spread_with_the_outermost_value_on_the_edge(count):
    """An interior gap's values split it into count + 1 equal parts; an edge gap's into count, the outermost on the
    edge."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)
    j = np.arange(1, count + 1)
    expected_values = [
        np.sort(_VALUES[0] - j * _VALUES[0] / count),  # left edge gap
        _VALUES[0] + j * (_VALUES[1] - _VALUES[0]) / (count + 1),  # interior gap
        _VALUES[2] + j * (1 - _VALUES[2]) / count,  # right edge gap
    ]

    # --- act --------------------------
    placement = MCTuplesGapPlacement(gaps, np.full(3, count))

    # --- assert -----------------------
    for gap, expected in enumerate(expected_values):
        assert placement.values(gap) == pytest.approx(expected)
    assert placement.spacings == pytest.approx([3.5 / count, 6.75 / (count + 1), 1012.5 / count])


@pytest.mark.parametrize("counts", [[1, 1, 1], [3, 2, 5], [2, 6, 1]])
def test_spacings_sums_and_offset_follow_from_the_values(counts):
    """Each gap's spacing is the distance between its consecutive values, its sum is their sum, and the offset is that
    of the mean of the size below's values and all new values."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- act --------------------------
    placement = MCTuplesGapPlacement(gaps, np.array(counts))

    # --- assert -----------------------
    all_values = [placement.values(gap) for gap in range(3)]
    assert placement.sums == pytest.approx([values.sum() for values in all_values])
    for gap, values in enumerate(all_values):
        if values.size > 1:
            assert np.diff(values) * N_FINE_LANES == pytest.approx(placement.spacings[gap])
    mean = np.concatenate([_VALUES, *all_values]).mean()
    assert placement.offset_fine_lanes == pytest.approx((mean - 0.5) * N_FINE_LANES)
    assert placement.corrected_min_spacing == pytest.approx(placement.spacings.min() - abs(placement.offset_fine_lanes))


@pytest.mark.parametrize("count", [0, -1])
def test_a_gap_without_new_tuples_has_no_values_no_sum_and_no_spacing(count):
    """A gap with 0 new tuples, or with -1 as the mean-aware search forms for a move out of an empty gap, has no
    values, adds nothing to the sum and gets an infinite spacing."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- act --------------------------
    placement = MCTuplesGapPlacement(gaps, np.full(3, count))

    # --- assert -----------------------
    assert all(placement.values(gap).size == 0 for gap in range(3))
    assert placement.sums.tolist() == [0.0, 0.0, 0.0]
    assert np.isinf(placement.spacings).all()
