"""The value correction:

- moves only the new tuples, or, for the smallest size, rotates each axis;
- brings the mean to exactly 0.5 when it can;
- nudges each new value to at least `MIN_N_BITS` bits;
- never puts 2 tuples in 1 fine lane.
"""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MIN_N_BITS, N_FINE_LANES, MCTuplesConstructionError, fine_lanes_of
from sunnbear._core.benchmark.mc_tuples.construction import correction as correction_module
from sunnbear._core.benchmark.mc_tuples.construction.correction import (
    CAP_RANGE,
    MCTuplesAxisValueCorrection,
    MCTuplesValueCorrection,
)
from sunnbear._core.utils.float_bits import n_bits


def _random_axis(seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Return the values of the size below and the new values of a random axis: each in its own fine lane, mostly near
    a lane's edge."""
    rng = np.random.default_rng(seed)
    size = int(rng.choice([32, 64, 256, 1024]))
    lanes = rng.choice(N_FINE_LANES, size=size, replace=False)
    # Positions concentrate near the lanes' edges, where the lane rules matter most; 0.999999 keeps them inside.
    values = (lanes + np.clip(rng.beta(0.2, 0.2, size=size), 1e-6, 0.999999)) / N_FINE_LANES
    n_required = int(rng.integers(0, size))
    return values[:n_required], values[n_required:]


def _limit_of(value: float, all_values: np.ndarray, is_move_left: bool) -> float:
    """Return the limit of a new value that moves left or right: the facing edge of its neighbor's fine lane on that
    side, measured across 0 and 1 for the lowest or the highest value, but never beyond 0 or 1."""
    if is_move_left:
        below = all_values[all_values < value]
        neighbor = below.max() if below.size else all_values.max() - 1.0
        return max((np.floor(neighbor * N_FINE_LANES) + 1) / N_FINE_LANES, 0.0)
    else:
        above = all_values[all_values > value]
        neighbor = above.min() if above.size else all_values.min() + 1.0
        return min(np.floor(neighbor * N_FINE_LANES) / N_FINE_LANES, 1.0)


@pytest.mark.parametrize("seed", range(40))
def test_the_correction_keeps_the_fine_lanes_the_order_and_the_size_below_and_moves_the_new_ones_1_way(seed):
    """On random axes, no fine lane ends with 2 tuples, the values of the size below and the order stay, every new
    tuple moves toward the same side apart from a nudge of a few float64 steps, no tuple moves more than halfway to its
    limit, and the mean reaches 0.5 unless the cap ends at its lower bound."""
    # --- arrange ----------------------
    required, new = _random_axis(seed)
    all_before = np.concatenate([required, new])

    # --- act --------------------------
    correction = MCTuplesAxisValueCorrection.of(required, new)

    # --- assert -----------------------
    all_after = np.concatenate([required, correction.corrected_new_values])
    assert np.bincount(fine_lanes_of(all_after)).max() == 1
    assert np.array_equal(np.argsort(all_before), np.argsort(all_after))
    moves = correction.corrected_new_values - new
    is_moved = np.abs(moves) > 1e-12
    assert np.all(moves[is_moved] <= 0) or np.all(moves[is_moved] >= 0)
    for value, move in zip(new[is_moved].tolist(), moves[is_moved].tolist(), strict=True):
        limit = _limit_of(value, all_before, is_move_left=move < 0)
        assert abs(move) <= 0.5 * abs(value - limit) + 1e-15
    assert np.all((all_after > 0) & (all_after < 1))
    assert correction.cap is not None
    if correction.cap > CAP_RANGE[0] + 1e-12:
        assert correction.offset_after_fine_lanes == pytest.approx(0.0, abs=1e-9)
        assert all_after.mean() == pytest.approx(0.5, abs=1e-12)


def test_the_correction_takes_the_shift_from_the_largest_spacings():
    """With the size below at 0.1 and 0.9 and new tuples at 0.3 and 0.75, a mean of 0.5 needs a left shift, and the
    cap shortens the wider spacing first: the tuple at 0.75 moves to 0.7, the cap D above its left neighbor at 0.3, and
    the tuple at 0.3, whose spacing to 0.1 lies below the cap, stays."""
    # --- arrange ----------------------
    required, new = np.array([0.1, 0.9]), np.array([0.3, 0.75])

    # --- act --------------------------
    correction = MCTuplesAxisValueCorrection.of(required, new)

    # --- assert -----------------------
    assert np.concatenate([required, correction.corrected_new_values]).mean() == pytest.approx(0.5)
    assert correction.offset_before_fine_lanes == pytest.approx((0.1 + 0.9 + 0.3 + 0.75) / 4 * N_FINE_LANES - 512)
    assert correction.corrected_new_values[0] == pytest.approx(0.3)  # its spacing to 0.1 lies below the cap
    assert correction.max_move_fine_lanes == pytest.approx(0.05 * N_FINE_LANES)
    assert correction.cap == pytest.approx(0.7 - 0.3)
    assert correction.rotation_shift is None


def test_the_correction_nudges_each_new_value_below_min_n_bits_within_its_fine_lane():
    """On an axis whose mean is already 0.5, a new value at a fine-lane center holds few bits; it moves by a few
    float64 steps to a value with at least `MIN_N_BITS` bits, in its own fine lane, and the mean stays 0.5."""
    # --- arrange ----------------------
    required = np.array([0.7718281828459045])
    new = np.array([200.5 / N_FINE_LANES, 0.0])
    new[1] = 1.5 - required[0] - new[0]  # This value has many bits and puts the mean at 0.5.
    new_lanes = fine_lanes_of(new)

    # --- act --------------------------
    correction = MCTuplesAxisValueCorrection.of(required, new)

    # --- assert -----------------------
    assert correction.n_nudged == 1
    assert n_bits(float(correction.corrected_new_values[0])) >= MIN_N_BITS
    assert correction.corrected_new_values[0] == pytest.approx(new[0], abs=1e-15)
    assert np.array_equal(fine_lanes_of(correction.corrected_new_values), new_lanes)
    assert np.concatenate([required, correction.corrected_new_values]).mean() == pytest.approx(0.5, abs=1e-12)


def test_the_nudge_refuses_a_value_whose_fine_lane_holds_no_value_with_min_n_bits_near_it(monkeypatch):
    """When the search for a value with `MIN_N_BITS` bits finds none in a value's fine lane, the correction raises an
    error."""
    # --- arrange ----------------------
    monkeypatch.setattr(correction_module, "nearest_float_with_min_n_bits", lambda *args: None)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="No value with at least"):
        MCTuplesAxisValueCorrection.of(np.array([0.25]), np.array([0.75]))


def test_a_correction_that_cannot_reach_0_5_ends_at_the_lower_cap_and_reports_the_rest():
    """When the size below holds a tuple at 0.9, a new tuple at 0.95 cannot reach 0.1, the value that a mean of 0.5
    needs: it stops at its floor, halfway to its limit, the right edge of the fine lane of the tuple at 0.9, and the
    correction reports the offset that remains."""
    # --- act --------------------------
    correction = MCTuplesAxisValueCorrection.of(np.array([0.9]), np.array([0.95]))

    # --- assert -----------------------
    limit = (np.floor(0.9 * N_FINE_LANES) + 1) / N_FINE_LANES
    floor = (0.95 + limit) / 2
    assert correction.cap == pytest.approx(CAP_RANGE[0], abs=1e-12)
    assert correction.corrected_new_values[0] == pytest.approx(floor, abs=1e-15)
    assert correction.offset_after_fine_lanes == pytest.approx((0.9 + floor) / 2 * N_FINE_LANES - 512)


def test_value_correction_corrects_both_axes_of_a_size():
    """The tuples of the size below come first and stay; both axes' means end at 0.5."""
    # --- arrange ----------------------
    tuple_array = np.array([[0.2, 0.8], [0.7, 0.3], [0.4, 0.65], [0.85, 0.15]])

    # --- act --------------------------
    correction = MCTuplesValueCorrection.of(tuple_array, n_required=2)

    # --- assert -----------------------
    assert correction.tuple_array[:2].tolist() == tuple_array[:2].tolist()
    assert correction.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5])
    assert correction.u.corrected_new_values.tolist() == correction.tuple_array[2:, 0].tolist()
    assert correction.v.corrected_new_values.tolist() == correction.tuple_array[2:, 1].tolist()


def test_value_correction_refuses_a_size_that_holds_2_tuples_in_1_fine_lane():
    """A tuple of the size below and a new tuple that share a fine lane, on an axis whose mean is already 0.5, still
    share it after the correction, which raises an error."""
    # --- arrange ----------------------
    required_u, new_u = 300.25 / N_FINE_LANES, 300.75 / N_FINE_LANES
    tuple_array = np.array([[required_u, 0.2], [0.6, 0.6], [new_u, 0.4], [2 - required_u - 0.6 - new_u, 0.8]])

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="a fine u-lane holds 2 tuples"):
        MCTuplesValueCorrection.of(tuple_array, n_required=2)


@pytest.mark.parametrize(
    "values, expected_shift",
    [
        # Mean 0.475: the shifts 0.025, 0.275, -0.475 and -0.225 give a mean of 0.5.
        ([0.1, 0.3, 0.6, 0.9], 0.025),
        # Mean 0.59975: the shifts 0.15025, 0.40025, -0.34975 and -0.09975 give a mean of 0.5.
        ([0.2, 0.4, 0.8, 0.999], -0.09975),
    ],
)
def test_the_rotation_takes_the_shift_nearest_to_0_that_gives_a_mean_of_0_5(values, expected_shift):
    """The rotation adds the same shift to every value, modulo 1, picks the shift nearest to 0 among those that give a
    mean of 0.5, and the nudge then moves each value by at most a few float64 steps."""
    # --- arrange ----------------------
    values = np.array(values)

    # --- act --------------------------
    correction = MCTuplesAxisValueCorrection.of_rotation_or_mean_correction(values)

    # --- assert -----------------------
    assert correction.cap is None
    assert correction.rotation_shift == pytest.approx(expected_shift)
    assert correction.corrected_new_values == pytest.approx((values + expected_shift) % 1.0, abs=1e-15)
    assert correction.corrected_new_values.mean() == pytest.approx(0.5, abs=1e-12)
    assert correction.offset_before_fine_lanes == pytest.approx((values.mean() - 0.5) * N_FINE_LANES)
    assert correction.max_move_fine_lanes == pytest.approx(abs(expected_shift) * N_FINE_LANES)


@pytest.mark.parametrize("seed", range(20))
def test_the_rotation_keeps_every_cyclic_distance_and_1_tuple_per_fine_lane(seed):
    """On random axes of the smallest size whose values lie more than 1 fine lane apart, the rotation keeps every value
    in a fine lane of its own, keeps every cyclic distance up to the nudge, and reaches a mean of 0.5."""
    # --- arrange ----------------------
    rng = np.random.default_rng(seed)
    # The values take every other fine lane, so that 2 values lie more than 1 fine lane apart and no shift puts them
    # into 1 fine lane.
    lanes = 2 * rng.choice(N_FINE_LANES // 2, size=32, replace=False)
    values = (lanes + rng.uniform(0.01, 0.99, size=32)) / N_FINE_LANES

    # --- act --------------------------
    correction = MCTuplesAxisValueCorrection.of_rotation_or_mean_correction(values)

    # --- assert -----------------------
    corrected = correction.corrected_new_values
    assert correction.rotation_shift is not None
    differences = np.abs(values[:, None] - values[None, :])
    corrected_differences = np.abs(corrected[:, None] - corrected[None, :])
    assert np.minimum(corrected_differences, 1 - corrected_differences) == pytest.approx(
        np.minimum(differences, 1 - differences), abs=1e-12
    )
    assert np.bincount(fine_lanes_of(corrected)).max() == 1
    assert corrected.mean() == pytest.approx(0.5, abs=1e-12)


def test_the_rotation_falls_back_to_the_mean_correction_when_it_would_put_2_tuples_in_1_fine_lane():
    """Values at 100.9 and 101.1 fine lanes, with a mean of 425.625 fine lanes, need a shift of 86.375 fine lanes plus a
    multiple of 256 fine lanes, the axis length over the 4 values; every such shift puts both values into 1 fine lane,
    so the axis gets the mean correction instead."""
    # --- arrange ----------------------
    values = np.array([100.9, 101.1, 700.3, 800.2]) / N_FINE_LANES

    # --- act --------------------------
    correction = MCTuplesAxisValueCorrection.of_rotation_or_mean_correction(values)

    # --- assert -----------------------
    assert correction.rotation_shift is None
    assert correction.cap is not None
    assert np.bincount(fine_lanes_of(correction.corrected_new_values)).max() == 1
    assert correction.corrected_new_values.mean() == pytest.approx(0.5, abs=1e-12)


def test_value_correction_rotates_both_axes_of_the_smallest_size():
    """Both axes of a size with no size below get a rotation, and both means end at 0.5."""
    # --- arrange ----------------------
    tuple_array = np.array([[0.1, 0.2], [0.3, 0.4], [0.6, 0.8], [0.9, 0.999]])

    # --- act --------------------------
    correction = MCTuplesValueCorrection.first_of(tuple_array, n_required=0)

    # --- assert -----------------------
    assert correction.u.rotation_shift == pytest.approx(0.025)
    assert correction.v.rotation_shift == pytest.approx(-0.09975)
    assert correction.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5], abs=1e-12)
    assert correction.u.corrected_new_values.tolist() == correction.tuple_array[:, 0].tolist()
    assert correction.v.corrected_new_values.tolist() == correction.tuple_array[:, 1].tolist()
