"""`MCTuplesAxisGapPlacement` spreads each gap's new tuples evenly, and derives its spacings, sums and mean from the
values of the new tuples."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES
from sunnbear._core.benchmark.mc_tuples.construction.allocation import MCTuplesAxisGaps
from sunnbear._core.benchmark.mc_tuples.construction.placement import MCTuplesAxisGapPlacement

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
    placement = MCTuplesAxisGapPlacement(gaps, np.full(3, count))

    # --- assert -----------------------
    for gap, expected in enumerate(expected_values):
        assert placement.values(gap) == pytest.approx(expected)
    assert placement.spacings == pytest.approx([3.5 / count, 6.75 / (count + 1), 1012.5 / count])


@pytest.mark.parametrize("counts", [[1, 1, 1], [3, 2, 5], [2, 6, 1]])
def test_spacings_sums_and_offset_follow_from_the_values(counts):
    """Each gap's spacing is the distance between its consecutive values, and its sum is the sum of those values; the
    offset is the mean of the size below's values and all new values, minus 0.5; and the corrected smallest spacing is
    the smallest spacing minus the absolute offset."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- act --------------------------
    placement = MCTuplesAxisGapPlacement(gaps, np.array(counts))

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
    """A gap with 0 new tuples, or with a count of -1, which the mean-aware search forms for a move out of an empty gap,
    has no values, adds nothing to the sum and gets an infinite spacing."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- act --------------------------
    placement = MCTuplesAxisGapPlacement(gaps, np.full(3, count))

    # --- assert -----------------------
    assert all(placement.values(gap).size == 0 for gap in range(3))
    assert placement.sums.tolist() == [0.0, 0.0, 0.0]
    assert np.isinf(placement.spacings).all()


def test_min_spacing_after_each_move_between_2_gaps_is_the_smaller_of_their_new_spacings():
    """With only 2 gaps, no other gap bounds the smallest spacing: an interior gap 500 fine lanes wide and a right edge
    gap 523.5 wide hold 2 and 3 new tuples, and their spacings end at:

    - 250 and 130.875 after a move to the right;
    - 125 and 261.75 after a move to the left.
    """
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(np.array([0.5, 500.5]) / N_FINE_LANES)
    placement = MCTuplesAxisGapPlacement(gaps, np.array([2, 3]))

    # --- act --------------------------
    min_spacings = placement._min_spacing_after_each_move()

    # --- assert -----------------------
    assert placement.spacings == pytest.approx([500.0 / 3, 523.5 / 3])
    assert min_spacings[0, 1] == pytest.approx(523.5 / 4)
    assert min_spacings[1, 0] == pytest.approx(500 / 4)


def test_corrected_min_spacing_after_each_move_matches_the_placement_after_that_move():
    """Each valid entry of the matrix equals `corrected_min_spacing` of the placement that the move leads to."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)
    counts = np.array([2, 3, 4])
    placement = MCTuplesAxisGapPlacement(gaps, counts)

    # --- act --------------------------
    matrix = placement.corrected_min_spacing_after_each_move()

    # --- assert -----------------------
    for source in range(3):
        for destination in range(3):
            if source != destination:
                counts_after_move = counts.copy()
                counts_after_move[source] -= 1
                counts_after_move[destination] += 1
                expected = MCTuplesAxisGapPlacement(gaps, counts_after_move).corrected_min_spacing
                assert matrix[source, destination] == pytest.approx(expected)
