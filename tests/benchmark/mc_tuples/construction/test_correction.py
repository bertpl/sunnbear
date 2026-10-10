"""The mean correction moves only the new tuples, brings the mean to exactly 0.5 when it can, and never puts 2 tuples
in 1 fine lane."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, MCTuplesConstructionError, fine_lanes_of
from sunnbear._core.benchmark.mc_tuples.construction.correction import CAP_RANGE, AxisMeanCorrection, MeanCorrection


def _random_axis(seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Return the old and the new values of a random axis: each in its own fine lane, mostly near a lane's edge."""
    rng = np.random.default_rng(seed)
    size = int(rng.choice([32, 64, 256, 1024]))
    lanes = rng.choice(N_FINE_LANES, size=size, replace=False)
    # Positions concentrate near the lanes' edges, where the lane rules matter most; 0.999999 keeps them inside.
    values = (lanes + np.clip(rng.beta(0.2, 0.2, size=size), 1e-6, 0.999999)) / N_FINE_LANES
    n_required = int(rng.integers(0, size))
    return values[:n_required], values[n_required:]


@pytest.mark.parametrize("seed", range(40))
def test_the_correction_keeps_the_fine_lanes_the_order_and_the_old_tuples_and_moves_the_new_ones_1_way(seed):
    """On random axes, no fine lane ends with 2 tuples, the old values and the order stay, every new tuple moves toward
    the same side, and the mean reaches 0.5 unless the cap ends at its lower bound."""
    # --- arrange ----------------------
    required, new = _random_axis(seed)

    # --- act --------------------------
    correction = AxisMeanCorrection.of(required, new)

    # --- assert -----------------------
    all_after = np.concatenate([required, correction.corrected_new_values])
    assert np.bincount(fine_lanes_of(all_after)).max() == 1
    assert np.array_equal(np.argsort(np.concatenate([required, new])), np.argsort(all_after))
    moves = correction.corrected_new_values - new
    assert np.all(moves <= 0) or np.all(moves >= 0)
    assert np.all((all_after > 0) & (all_after < 1))
    if correction.cap > CAP_RANGE[0] * 1.001:
        assert correction.offset_after_fine_lanes == pytest.approx(0.0, abs=1e-9)
        assert all_after.mean() == pytest.approx(0.5, abs=1e-12)


def test_the_correction_takes_the_shift_from_the_largest_gaps():
    """With new tuples at 0.3 and 0.75 above an old tuple at 0.1, a mean of 0.5 needs a left shift, and the cap
    shortens the wider gap first: the tuple at 0.75 moves to 0.7, and the tuple at 0.3, whose gap to 0.1 lies below
    the cap, stays."""
    # --- arrange ----------------------
    required, new = np.array([0.1, 0.9]), np.array([0.3, 0.75])

    # --- act --------------------------
    correction = AxisMeanCorrection.of(required, new)

    # --- assert -----------------------
    assert np.concatenate([required, correction.corrected_new_values]).mean() == pytest.approx(0.5)
    assert correction.offset_before_fine_lanes == pytest.approx((0.1 + 0.9 + 0.3 + 0.75) / 4 * N_FINE_LANES - 512)
    assert correction.corrected_new_values[0] == pytest.approx(0.3)  # its gap to 0.1 lies below the cap
    assert correction.max_move_fine_lanes == pytest.approx(0.05 * N_FINE_LANES)


def test_a_correction_that_cannot_reach_0_5_ends_at_the_lower_cap_and_reports_the_rest():
    """A new tuple at 0.95 above an old one at 0.9 cannot reach 0.1, the value that a mean of 0.5 needs: it stops just
    above the old tuple's fine lane, and the correction reports the offset that remains."""
    # --- act --------------------------
    correction = AxisMeanCorrection.of(np.array([0.9]), np.array([0.95]))

    # --- assert -----------------------
    lane_above_old = (np.floor(0.9 * N_FINE_LANES) + 1) / N_FINE_LANES
    assert correction.cap == pytest.approx(CAP_RANGE[0])
    assert correction.corrected_new_values[0] == pytest.approx(lane_above_old)
    assert correction.offset_after_fine_lanes == pytest.approx((0.9 + lane_above_old) / 2 * N_FINE_LANES - 512)


def test_mean_correction_corrects_both_axes_of_a_size():
    """The size's old tuples come first and stay; both axes' means end at 0.5."""
    # --- arrange ----------------------
    tuple_array = np.array([[0.2, 0.8], [0.7, 0.3], [0.45, 0.65], [0.95, 0.15]])

    # --- act --------------------------
    correction = MeanCorrection.of(tuple_array, n_required=2)

    # --- assert -----------------------
    assert correction.tuple_array[:2].tolist() == tuple_array[:2].tolist()
    assert correction.tuple_array.mean(axis=0) == pytest.approx([0.5, 0.5])
    assert correction.u.corrected_new_values.tolist() == correction.tuple_array[2:, 0].tolist()
    assert correction.v.corrected_new_values.tolist() == correction.tuple_array[2:, 1].tolist()


def test_mean_correction_refuses_a_size_that_holds_2_tuples_in_1_fine_lane():
    """An old and a new tuple that share a fine lane, on an axis whose mean is already 0.5, still share it after the
    correction, which raises an error."""
    # --- arrange ----------------------
    old_u, new_u = 300.25 / N_FINE_LANES, 300.75 / N_FINE_LANES
    tuple_array = np.array([[old_u, 0.2], [0.6, 0.6], [new_u, 0.4], [2 - old_u - 0.6 - new_u, 0.8]])

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="a fine u-lane holds 2 tuples"):
        MeanCorrection.of(tuple_array, n_required=2)
