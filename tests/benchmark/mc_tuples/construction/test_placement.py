"""`MCTuplesAxisGapPlacement` spreads each gap's new tuples evenly, the 2 edge gaps' together over the wrap-around gap,
and derives its spacings, sums and mean from the values of the new tuples."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES
from sunnbear._core.benchmark.mc_tuples.construction.allocation import MCTuplesAxisGaps
from sunnbear._core.benchmark.mc_tuples.construction.placement import MCTuplesAxisGapPlacement

# The tuples of the size below lie in fine lanes 3, 10 and 11, which leaves a left edge gap below 3.5, an interior gap
# between 3.5 and 10.25, and a right edge gap above 11.5, in fine lanes. The 2 edge gaps form the wrap-around gap, from
# 11.5 up to 1024 and on from 0 to 3.5.
_VALUES = np.array([3.5, 10.25, 11.5]) / N_FINE_LANES


@pytest.mark.parametrize("count", [1, 2, 3])
def test_an_interior_gap_splits_the_stretch_between_its_neighbors_values_into_count_plus_1_equal_parts(count):
    """An interior gap's `count` new values split the stretch between its 2 neighboring values into count + 1 equal
    parts."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)
    j = np.arange(1, count + 1)
    expected_values = _VALUES[0] + j * (_VALUES[1] - _VALUES[0]) / (count + 1)

    # --- act --------------------------
    placement = MCTuplesAxisGapPlacement(gaps, np.array([0, count, 0]))

    # --- assert -----------------------
    assert placement.values(1) == pytest.approx(expected_values)
    assert placement.spacings[1] == pytest.approx(6.75 / (count + 1))


@pytest.mark.parametrize(
    "required_values, counts, expected_left, expected_right, expected_spacing",
    [
        # Edge gaps 250 and 150 wide: their 3 values split the wrap-around gap of 400 into 4 parts of 100.
        ([250.0, 874.0], [2, 0, 1], [50.0, 150.0], [974.0], 100.0),
        # An even split of the wrap-around gap of 390 into 5 parts of 78 puts only 1 of the right edge gap's 3 values
        # below 1024. They split the right edge gap, 90 wide, into 3 parts of 30, the highest on 1024; the left edge
        # gap's 1 value splits the left edge gap, 300 wide, into 2 parts of 150.
        ([300.0, 934.0], [1, 0, 3], [150.0], [964.0, 994.0, 1024.0], 30.0),
        # The same with the 2 edge gaps swapped: the left edge gap's 3 values start on 0.
        ([90.0, 724.0], [3, 0, 1], [0.0, 30.0, 60.0], [874.0], 30.0),
    ],
)
def test_edge_gaps_split_the_wrap_around_gap_evenly_unless_1_edge_gap_holds_too_many_values(
    required_values, counts, expected_left, expected_right, expected_spacing
):
    """The 2 edge gaps' new values split the wrap-around gap into equal parts, unless 1 edge gap holds too many values
    for that split; both edge gaps report the smallest distance between neighboring values on the wrap-around gap."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(np.array(required_values) / N_FINE_LANES)

    # --- act --------------------------
    placement = MCTuplesAxisGapPlacement(gaps, np.array(counts))

    # --- assert -----------------------
    assert placement.values(0) * N_FINE_LANES == pytest.approx(expected_left)
    assert placement.values(2) * N_FINE_LANES == pytest.approx(expected_right)
    assert placement.spacings[[0, 2]] == pytest.approx([expected_spacing, expected_spacing])


@pytest.mark.parametrize(
    "required_values, counts, edge_gap, expected_values",
    [
        # No left edge gap: the wrap-around gap runs from 500.5 up to 1024 and on to 0.5.
        ([0.5, 500.5], [0, 3], 1, [631.5, 762.5, 893.5]),
        # No right edge gap: the wrap-around gap runs from 1023.5 up to 1024 and on to 523.5.
        ([523.5, 1023.5], [3, 0], 0, [130.5, 261.5, 392.5]),
    ],
)
def test_a_lone_edge_gap_spreads_its_values_over_the_whole_wrap_around_gap(
    required_values, counts, edge_gap, expected_values
):
    """With a value of the size below in 1 outer fine lane, only the other edge gap forms; its 3 values split the whole
    wrap-around gap, 524 fine lanes up to that value, into 4 parts of 131."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(np.array(required_values) / N_FINE_LANES)

    # --- act --------------------------
    placement = MCTuplesAxisGapPlacement(gaps, np.array(counts))

    # --- assert -----------------------
    assert gaps.edge_gaps.tolist() == [edge_gap]
    assert placement.values(edge_gap) * N_FINE_LANES == pytest.approx(expected_values)
    assert placement.spacings[edge_gap] == pytest.approx(131.0)


@pytest.mark.parametrize("counts", [[1, 1, 1], [3, 2, 5], [2, 6, 1]])
def test_spacings_sums_and_offset_follow_from_the_values(counts):
    """Every prediction follows from the values of the new tuples:

    - the interior gap's spacing is the distance between its consecutive values, its 2 bounds included;
    - each edge gap's spacing is the smallest distance between consecutive values on the wrap-around gap, from the
      highest value of the size below up to 1 and on from 0 to the lowest;
    - each gap's sum is the sum of its values;
    - the offset is the mean of the size below's values and all new values, minus 0.5, in fine lanes;
    - the corrected smallest spacing is the smallest spacing minus the absolute offset times the number of all values
      divided by the number of new values.
    """
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- act --------------------------
    placement = MCTuplesAxisGapPlacement(gaps, np.array(counts))

    # --- assert -----------------------
    all_values = [placement.values(gap) for gap in range(3)]
    assert placement.sums == pytest.approx([values.sum() for values in all_values])
    interior_gap = np.concatenate([[_VALUES[0]], all_values[1], [_VALUES[1]]])
    assert np.diff(interior_gap) * N_FINE_LANES == pytest.approx(placement.spacings[1])
    # Adding 1 to the left edge gap's values and to the lowest value lays the wrap-around gap out in ascending order.
    wrap_around_gap = np.concatenate([[_VALUES[2]], all_values[2], all_values[0] + 1, [_VALUES[0] + 1]])
    assert placement.spacings[[0, 2]] == pytest.approx(np.diff(wrap_around_gap).min() * N_FINE_LANES)
    mean = np.concatenate([_VALUES, *all_values]).mean()
    assert placement.offset_fine_lanes == pytest.approx((mean - 0.5) * N_FINE_LANES)
    weight = (_VALUES.size + sum(counts)) / sum(counts)
    assert placement.offset_weight == pytest.approx(weight)
    assert placement.corrected_min_spacing == pytest.approx(
        placement.spacings.min() - weight * abs(placement.offset_fine_lanes)
    )


@pytest.mark.parametrize("count", [0, -1])
def test_a_gap_without_new_tuples_has_no_values_no_sum_and_no_spacing(count):
    """A gap with 0 new tuples has no values, adds nothing to the sum and gets an infinite spacing; so does a gap with a
    count of -1, which the mean-aware search forms for a move out of an empty gap."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- act --------------------------
    placement = MCTuplesAxisGapPlacement(gaps, np.full(3, count))

    # --- assert -----------------------
    assert all(placement.values(gap).size == 0 for gap in range(3))
    assert placement.sums.tolist() == [0.0, 0.0, 0.0]
    assert np.isinf(placement.spacings).all()


def test_spacings_after_adding_1_match_the_placement_with_1_more_tuple_in_that_gap():
    """Each entry of `spacings_after_adding_1` equals that gap's spacing in the placement with 1 more new tuple in that
    gap alone."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)
    counts = np.array([2, 3, 4])
    placement = MCTuplesAxisGapPlacement(gaps, counts)

    # --- act --------------------------
    spacings_after_adding_1 = placement.spacings_after_adding_1()

    # --- assert -----------------------
    for gap in range(3):
        counts_after_adding_1 = counts.copy()
        counts_after_adding_1[gap] += 1
        expected = MCTuplesAxisGapPlacement(gaps, counts_after_adding_1).spacings[gap]
        assert spacings_after_adding_1[gap] == pytest.approx(expected)


def test_min_spacing_after_each_move_between_2_gaps_is_the_smaller_of_their_new_spacings():
    """With only 2 gaps, no other gap bounds the smallest spacing: 2 interior gaps 500 and 523 fine lanes wide hold 2
    and 3 new tuples, and their spacings end at:

    - 250 and 104.6 after a move to the right;
    - 125 and 174.33 after a move to the left.

    The size below fills both outer fine lanes, so that no edge gap forms: `_min_spacing_after_each_move` leaves the
    entries of moves into or out of an edge gap to `corrected_min_spacing_after_each_move`.
    """
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(np.array([0.5, 500.5, 1023.5]) / N_FINE_LANES)
    placement = MCTuplesAxisGapPlacement(gaps, np.array([2, 3]))

    # --- act --------------------------
    min_spacings = placement._min_spacing_after_each_move()

    # --- assert -----------------------
    assert placement.spacings == pytest.approx([500.0 / 3, 523.0 / 4])
    assert min_spacings[0, 1] == pytest.approx(523.0 / 5)
    assert min_spacings[1, 0] == pytest.approx(500.0 / 4)


def test_corrected_min_spacing_after_each_move_matches_the_placement_after_that_move():
    """Each entry `[s, d]` of `corrected_min_spacing_after_each_move`, for `s` other than `d`, equals
    `corrected_min_spacing` of the placement after moving 1 tuple from gap `s` to gap `d`."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)
    counts = np.array([2, 3, 4])
    placement = MCTuplesAxisGapPlacement(gaps, counts)

    # --- act --------------------------
    corrected_min_spacings = placement.corrected_min_spacing_after_each_move()

    # --- assert -----------------------
    for source in range(3):
        for destination in range(3):
            if source != destination:
                expected = placement.after_move(source, destination).corrected_min_spacing
                assert corrected_min_spacings[source, destination] == pytest.approx(expected)
