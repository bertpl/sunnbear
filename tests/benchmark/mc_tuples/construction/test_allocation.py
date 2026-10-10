"""`MCTuplesAxisGaps` finds the gaps of free fine lanes and predicts their spacing and values;
`MCTuplesAxisGapAllocation` allocates new tuples to the gaps so that the predicted mean lies close to 0.5."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, fine_lanes_of
from sunnbear._core.benchmark.mc_tuples.construction.allocation import MCTuplesAxisGapAllocation, MCTuplesAxisGaps

# The tuples of the size below lie in fine lanes 3, 10 and 11, which leaves a left edge gap [0, 3), an interior gap
# [4, 10), no gap between 10 and 11, and a right edge gap [12, 1024).
_VALUES = np.array([3.5, 10.25, 11.5]) / N_FINE_LANES

# Spreading the 32 tuples of the size below from the first fine lane to the last leaves 31 gaps for 32 new tuples,
# so 1 gap gets 2.
_SPREAD_VALUES = (np.round(np.linspace(0, N_FINE_LANES - 1, 32)) + 0.5) / N_FINE_LANES


# ==================================================================================================
#  MCTuplesAxisGaps
# ==================================================================================================
def test_of_finds_the_gaps_with_their_widths_edges_and_bounds():
    """Each maximal run of free fine lanes is a gap with its width, edge flags and bounds; adjacent lanes leave none."""
    # --- act --------------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- assert -----------------------
    assert gaps.first_lanes.tolist() == [0, 4, 12]
    assert gaps.n_free_lanes.tolist() == [3, 6, 1012]
    assert gaps.widths.tolist() == [3.0, 7.0, 1012.0]
    assert gaps.is_left_edge.tolist() == [True, False, False]
    assert gaps.is_right_edge.tolist() == [False, False, True]
    assert gaps.lows.tolist() == [0.0, _VALUES[0], _VALUES[2]]
    assert gaps.highs.tolist() == [_VALUES[0], _VALUES[1], 1.0]
    assert gaps.n_required == 3
    assert gaps.required_sum == pytest.approx(_VALUES.sum())


def test_of_leaves_out_an_edge_gap_when_a_tuple_of_the_size_below_lies_in_the_outermost_fine_lane():
    """A tuple of the size below in fine lane 0 leaves no left edge gap."""
    # --- act --------------------------
    gaps = MCTuplesAxisGaps.of(np.array([0.5, 500.5]) / N_FINE_LANES)

    # --- assert -----------------------
    assert gaps.first_lanes.tolist() == [1, 501]
    assert not gaps.is_left_edge.any()


@pytest.mark.parametrize("count", [1, 2, 3])
def test_predicted_sums_and_spacings_follow_an_even_spread_with_the_outermost_value_on_the_edge(count):
    """An interior gap's values split it into count + 1 equal parts; an edge gap's into count, the outermost on the
    edge."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)
    low, high = _VALUES[0], _VALUES[1]
    j = np.arange(1, count + 1)
    expected_values = [
        _VALUES[0] - j * _VALUES[0] / count,  # left edge gap
        low + j * (high - low) / (count + 1),  # interior gap
        _VALUES[2] + j * (1 - _VALUES[2]) / count,  # right edge gap
    ]

    # --- act --------------------------
    sums = gaps.predicted_sums(np.full(3, count))
    spacings = gaps.spacings(np.full(3, count))

    # --- assert -----------------------
    assert sums == pytest.approx([values.sum() for values in expected_values])
    assert spacings == pytest.approx([3 / count, 7 / (count + 1), 1012 / count])


def test_an_empty_gap_has_no_predicted_values_and_no_spacing():
    """A gap without new tuples adds nothing to the predicted sum and gets an infinite spacing."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_VALUES)

    # --- act / assert -----------------
    assert gaps.predicted_sums(np.zeros(3, dtype=np.int64)).tolist() == [0.0, 0.0, 0.0]
    assert np.isinf(gaps.spacings(np.zeros(3, dtype=np.int64))).all()


def test_greedy_counts_give_each_new_tuple_to_the_gap_that_keeps_the_widest_spacing():
    """Gaps of widths 100 (left edge), 500 and 423 (right edge) take 3 new tuples as: right, interior, right."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(np.array([100.5, 600.5]) / N_FINE_LANES)

    # --- act / assert -----------------
    assert gaps.greedy_counts(3).tolist() == [0, 1, 2]


def test_greedy_counts_give_a_gap_at_most_1_new_tuple_per_free_fine_lane():
    """With as many new tuples as free fine lanes, every gap fills up, the narrow edge gaps included."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(np.array([3.5, 1020.5]) / N_FINE_LANES)

    # --- act --------------------------
    counts = gaps.greedy_counts(int(gaps.n_free_lanes.sum()))

    # --- assert -----------------------
    assert counts.tolist() == gaps.n_free_lanes.tolist()


def test_mean_aware_counts_move_the_extra_tuple_to_the_middle_gap_without_lowering_the_smallest_spacing():
    """With 31 equal gaps for 32 new tuples, the greedy allocation gives 2 new tuples to the first gap, which puts the
    predicted mean 7.7 fine lanes from 0.5; the mean-aware allocation gives 2 to the middle gap instead, which brings
    the predicted mean to 0.5."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(_SPREAD_VALUES)
    greedy_counts = gaps.greedy_counts(32)

    # --- act --------------------------
    counts = gaps.mean_aware_counts(greedy_counts)

    # --- assert -----------------------
    assert gaps.predicted_offset_fine_lanes(greedy_counts) == pytest.approx(-7.734375)
    assert gaps.predicted_offset_fine_lanes(counts) == pytest.approx(0.0, abs=1e-9)
    assert np.flatnonzero(counts == 2).tolist() == [15]
    assert counts.sum() == 32
    assert gaps.spacings(counts).min() == gaps.spacings(greedy_counts).min()


def test_mean_aware_counts_keep_an_allocation_that_fills_every_free_fine_lane():
    """With as many new tuples as free fine lanes, no gap can take another, so the greedy allocation stays."""
    # --- arrange ----------------------
    gaps = MCTuplesAxisGaps.of(np.array([3.5, 1020.5]) / N_FINE_LANES)
    greedy_counts = gaps.greedy_counts(int(gaps.n_free_lanes.sum()))

    # --- act / assert -----------------
    assert gaps.mean_aware_counts(greedy_counts).tolist() == greedy_counts.tolist()


def test_mean_aware_counts_end_where_no_single_move_raises_the_corrected_min_spacing():
    """With random values for the size below, the search ends at an allocation that fits every gap's free fine lanes,
    whose `predicted_corrected_min_spacing` is at least the greedy allocation's, and whose
    `predicted_corrected_min_spacing` no move of 1 new tuple to another gap raises."""
    # --- arrange ----------------------
    values = np.random.default_rng(3).choice(N_FINE_LANES, size=128, replace=False) / N_FINE_LANES + 0.4 / N_FINE_LANES
    gaps = MCTuplesAxisGaps.of(values)
    greedy_counts = gaps.greedy_counts(128)

    # --- act --------------------------
    counts = gaps.mean_aware_counts(greedy_counts)

    # --- assert -----------------------
    assert counts.sum() == 128
    assert np.all(counts <= gaps.n_free_lanes)
    corrected_min_spacing = gaps.predicted_corrected_min_spacing(counts)
    assert corrected_min_spacing >= gaps.predicted_corrected_min_spacing(greedy_counts)
    for source in np.flatnonzero(counts >= 1):
        for destination in np.flatnonzero(counts < gaps.n_free_lanes):
            if destination != source:
                counts_after_move = counts.copy()
                counts_after_move[source] -= 1
                counts_after_move[destination] += 1
                assert gaps.predicted_corrected_min_spacing(counts_after_move) <= corrected_min_spacing


# ==================================================================================================
#  MCTuplesAxisGapAllocation
# ==================================================================================================
def test_allocation_without_a_size_below_is_1_gap_of_all_fine_lanes():
    """The smallest size has no size below, so every fine lane belongs to 1 gap that gets every new tuple."""
    # --- act --------------------------
    allocation = MCTuplesAxisGapAllocation.of(np.zeros(0), 32)

    # --- assert -----------------------
    assert allocation.counts.tolist() == [32]
    assert allocation.gap_of_fine_lane.tolist() == [0] * N_FINE_LANES
    assert allocation.greedy_offset_fine_lanes is None
    assert allocation.mean_aware_offset_fine_lanes is None


def test_allocation_numbers_the_gaps_with_new_tuples_and_leaves_the_others_out():
    """Each fine lane of a gap with new tuples maps to that gap; occupied fine lanes and empty gaps map to -1."""
    # --- act --------------------------
    allocation = MCTuplesAxisGapAllocation.of(_SPREAD_VALUES, 32)

    # --- assert -----------------------
    occupied = fine_lanes_of(_SPREAD_VALUES)
    assert np.all(allocation.gap_of_fine_lane[occupied] == -1)
    assert allocation.counts.sum() == 32
    assert allocation.greedy_offset_fine_lanes == pytest.approx(-7.734375)
    assert allocation.mean_aware_offset_fine_lanes == pytest.approx(0.0, abs=1e-9)
