"""`AxisGaps` finds the gaps of free fine lanes and predicts their spacing and values; `GapAllocation` allocates new
tuples to them with the mean in mind."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES
from sunnbear._core.benchmark.mc_tuples.construction_gaps import AxisGaps, GapAllocation

# Old tuples in fine lanes 3, 10 and 11: a left edge gap [0, 3), an interior gap [4, 10), no gap between 10 and 11,
# and a right edge gap [12, 1024).
_VALUES = np.array([3.5, 10.25, 11.5]) / N_FINE_LANES

# 32 old tuples from the first fine lane to the last leave 31 interior gaps for 32 new tuples, so 1 gap gets 2.
_SPREAD_VALUES = (np.round(np.linspace(0, N_FINE_LANES - 1, 32)) + 0.5) / N_FINE_LANES


# ==================================================================================================
#  AxisGaps
# ==================================================================================================
def test_of_finds_the_gaps_with_their_widths_edges_and_bounds():
    """Each maximal run of free fine lanes is a gap, adjacent occupied fine lanes leave none, and the edge gaps reach the
    edges of the axis."""
    # --- act --------------------------
    gaps = AxisGaps.of(_VALUES)

    # --- assert -----------------------
    assert gaps.first_lanes.tolist() == [0, 4, 12]
    assert gaps.n_free.tolist() == [3, 6, 1012]
    assert gaps.widths.tolist() == [3.0, 7.0, 1012.0]
    assert gaps.is_left_edge.tolist() == [True, False, False]
    assert gaps.is_right_edge.tolist() == [False, False, True]
    assert gaps.lows.tolist() == [0.0, _VALUES[0], _VALUES[2]]
    assert gaps.highs.tolist() == [_VALUES[0], _VALUES[1], 1.0]
    assert gaps.n_required == 3
    assert gaps.required_sum == pytest.approx(_VALUES.sum())


def test_of_leaves_out_an_edge_gap_when_an_old_tuple_lies_in_the_outermost_fine_lane():
    """An old tuple in fine lane 0 leaves no left edge gap."""
    # --- act --------------------------
    gaps = AxisGaps.of(np.array([0.5, 500.5]) / N_FINE_LANES)

    # --- assert -----------------------
    assert gaps.first_lanes.tolist() == [1, 501]
    assert not gaps.is_left_edge.any()


@pytest.mark.parametrize("count", [1, 2, 3])
def test_predicted_sums_and_spacings_follow_an_even_spread_with_the_outermost_value_on_the_edge(count):
    """An interior gap's values split it into count + 1 equal parts; an edge gap's into count, the outermost on the
    edge."""
    # --- arrange ----------------------
    gaps = AxisGaps.of(_VALUES)
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
    # --- act / assert -----------------
    gaps = AxisGaps.of(_VALUES)
    assert gaps.predicted_sums(np.zeros(3, dtype=np.int64)).tolist() == [0.0, 0.0, 0.0]
    assert np.isinf(gaps.spacings(np.zeros(3, dtype=np.int64))).all()


def test_greedy_counts_give_each_new_tuple_to_the_gap_that_keeps_the_widest_spacing():
    """Gaps of widths 100 (left edge), 500 and 423 (right edge) take 3 new tuples as: right, interior, right."""
    # --- arrange ----------------------
    gaps = AxisGaps.of(np.array([100.5, 600.5]) / N_FINE_LANES)

    # --- act / assert -----------------
    assert gaps.greedy_counts(3).tolist() == [0, 1, 2]


def test_greedy_counts_give_a_gap_at_most_1_new_tuple_per_free_fine_lane():
    """With as many new tuples as free fine lanes, every gap fills up, the narrow edge gaps included."""
    # --- arrange ----------------------
    gaps = AxisGaps.of(np.array([3.5, 1020.5]) / N_FINE_LANES)

    # --- act --------------------------
    counts = gaps.greedy_counts(int(gaps.n_free.sum()))

    # --- assert -----------------------
    assert counts.tolist() == gaps.n_free.tolist()


def test_balanced_counts_move_the_extra_tuple_to_the_middle_gap_without_lowering_the_smallest_spacing():
    """With 31 equal gaps for 32 new tuples, the greedy allocation doubles the first gap, 7.7 fine lanes off; the
    mean-aware allocation doubles the middle gap instead, which brings the predicted mean to 0.5."""
    # --- arrange ----------------------
    gaps = AxisGaps.of(_SPREAD_VALUES)
    greedy_counts = gaps.greedy_counts(32)

    # --- act --------------------------
    counts = gaps.balanced_counts(greedy_counts, epsilon=0.1)

    # --- assert -----------------------
    assert gaps.predicted_offset_fine_lanes(greedy_counts) == pytest.approx(-7.734375)
    assert gaps.predicted_offset_fine_lanes(counts) == pytest.approx(0.0, abs=1e-9)
    assert np.flatnonzero(counts == 2).tolist() == [15]
    assert counts.sum() == 32
    assert gaps.spacings(counts).min() == gaps.spacings(greedy_counts).min()


def test_balanced_counts_keep_every_spacing_within_the_floor():
    """No gap's spacing falls below (1 − ε) times the greedy allocation's smallest spacing, and no gap takes more new
    tuples than it has free fine lanes."""
    # --- arrange ----------------------
    values = np.random.default_rng(3).choice(N_FINE_LANES, size=128, replace=False) / N_FINE_LANES + 0.4 / N_FINE_LANES
    gaps = AxisGaps.of(values)
    greedy_counts = gaps.greedy_counts(128)

    # --- act --------------------------
    counts = gaps.balanced_counts(greedy_counts, epsilon=0.1)

    # --- assert -----------------------
    assert counts.sum() == 128
    assert np.all(counts <= gaps.n_free)
    assert gaps.spacings(counts).min() >= 0.9 * gaps.spacings(greedy_counts).min()
    assert abs(gaps.predicted_offset_fine_lanes(counts)) <= abs(gaps.predicted_offset_fine_lanes(greedy_counts))


# ==================================================================================================
#  GapAllocation
# ==================================================================================================
def test_allocation_without_a_size_below_is_1_gap_of_all_fine_lanes():
    """The smallest size has no old tuples, so every fine lane belongs to 1 gap that gets every new tuple."""
    # --- act --------------------------
    allocation = GapAllocation.of(np.zeros(0), 32, epsilon=0.1)

    # --- assert -----------------------
    assert allocation.counts.tolist() == [32]
    assert allocation.widths.tolist() == [N_FINE_LANES]
    assert allocation.greedy_offset_fine_lanes is None
    assert allocation.predicted_offset_fine_lanes is None


def test_allocation_numbers_the_gaps_with_new_tuples_and_leaves_the_others_out():
    """Each fine lane of a gap with new tuples maps to that gap; occupied fine lanes and empty gaps map to -1."""
    # --- act --------------------------
    allocation = GapAllocation.of(_SPREAD_VALUES, 32, epsilon=0.1)

    # --- assert -----------------------
    occupied = np.floor(_SPREAD_VALUES * N_FINE_LANES).astype(np.int64)
    assert np.all(allocation.gap_of_fine_lane[occupied] == -1)
    assert allocation.counts.sum() == 32
    assert allocation.widths.sum() == np.count_nonzero(allocation.gap_of_fine_lane >= 0)
    assert allocation.greedy_offset_fine_lanes == pytest.approx(-7.734375)
    assert allocation.predicted_offset_fine_lanes == pytest.approx(0.0, abs=1e-9)
