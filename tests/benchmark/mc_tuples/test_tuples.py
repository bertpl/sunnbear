"""`MCTuples` validates and stores a tuple set, maps it onto a test function, and reports its spread."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.benchmark.mc_tuples.tuples import axis_bin_indices

# The diagonal set has 8 tuples, one per bin on each axis: u rises and v falls, so neighbors are diagonal at L2
# distance √2/8.
_DIAGONAL_U = (np.arange(8) + 0.5) / 8
_DIAGONAL_V = _DIAGONAL_U[::-1]


# ==================================================================================================
#  Construction and values
# ==================================================================================================
@pytest.mark.parametrize(
    "u, v, message",
    [
        ([0.1, 0.2], [0.1], "equal length"),
        ([[0.1, 0.2]], [[0.1, 0.2]], "1-D"),
        ([0.1], [0.1], "at least 2"),
        ([0.0, 0.5], [0.1, 0.2], "open interval"),
        ([0.1, 0.5], [0.1, 1.0], "open interval"),
    ],
)
def test_mc_tuples_class_rejects_invalid_values(u, v, message):
    """Arrays of different shapes, fewer than 2 tuples, or a value outside (0, 1) raise a `ValueError`."""
    with pytest.raises(ValueError, match=message):
        MCTuples(u, v)


def test_mc_tuples_class_stores_read_only_copies():
    """Changing the input array later leaves the tuples unchanged, and the stored arrays cannot be written."""
    # --- arrange ----------------------
    u = np.array([0.1, 0.2])
    tuples = MCTuples(u, [0.3, 0.4])

    # --- act --------------------------
    u[0] = 0.9

    # --- assert -----------------------
    assert tuples.u.tolist() == [0.1, 0.2]
    assert tuples.size == 2
    with pytest.raises(ValueError, match="read-only"):
        tuples.v[0] = 0.5


def test_first_returns_the_leading_tuples():
    """`first(size)` returns the first `size` tuples, in order."""
    # --- arrange ----------------------
    tuples = MCTuples(_DIAGONAL_U, _DIAGONAL_V)

    # --- act --------------------------
    first_3 = tuples.first(3)

    # --- assert -----------------------
    assert first_3.u.tolist() == _DIAGONAL_U[:3].tolist()
    assert first_3.v.tolist() == _DIAGONAL_V[:3].tolist()


@pytest.mark.parametrize("size", [1, 9])
def test_first_rejects_a_size_outside_the_set(size):
    """A size below 2 or above the set's size raises a `ValueError`."""
    with pytest.raises(ValueError, match="size must lie in"):
        MCTuples(_DIAGONAL_U, _DIAGONAL_V).first(size)


def test_to_xtol_and_c_maps_u_log_uniformly_and_v_linearly():
    """u = 0.5 lands at `xtol_min · √2`, and v places c linearly between `c_min` and `c_max`."""
    # --- arrange ----------------------
    tuples = MCTuples([0.5, 0.25], [0.5, 0.25])

    # --- act --------------------------
    xtol, c = tuples.to_xtol_and_c(xtol_min=1e-6, c_min=-2.0, c_max=2.0)

    # --- assert -----------------------
    assert xtol == pytest.approx([1e-6 * np.sqrt(2), 1e-6 * 2**0.25])
    assert c == pytest.approx([0.0, -1.0])


# ==================================================================================================
#  Stats
# ==================================================================================================
def test_stats_reports_bin_counts_and_min_separations():
    """One tuple per bin gives counts of 1, separations 1/8 per axis and √2/8 in L2, and their fractions."""
    # --- act --------------------------
    stats = MCTuples(_DIAGONAL_U, _DIAGONAL_V).stats()

    # --- assert -----------------------
    assert stats.size == 8
    assert stats.bin_counts_u == (1,) * 8
    assert stats.bin_counts_v == (1,) * 8
    assert stats.max_bin_count_deviation == 0
    assert stats.min_separation_u == pytest.approx(1 / 8)
    assert stats.min_separation_v == pytest.approx(1 / 8)
    assert stats.min_separation_l2 == pytest.approx(np.sqrt(2) / 8)
    assert stats.min_separation_u_fraction == pytest.approx(7 / 8)
    assert stats.min_separation_v_fraction == pytest.approx(7 / 8)
    assert stats.min_separation_l2_fraction == pytest.approx(np.sqrt(2) / 8 * (np.sqrt(8) - 1))


def test_max_bin_count_deviation_is_the_largest_over_both_axes():
    """Putting 3 of 8 tuples in one bin of v, where 1 is expected, gives a deviation of 2."""
    # --- arrange ----------------------
    v = np.array([0.01, 0.02, 0.03, 0.4, 0.5, 0.6, 0.7, 0.8])

    # --- act / assert -----------------
    assert MCTuples(_DIAGONAL_U, v).stats().max_bin_count_deviation == 2


def test_axis_bin_indices_puts_each_value_in_its_eighth_of_the_axis():
    """A value in [s/8, (s+1)/8) is in bin s, and a value just below 1 is in the last bin."""
    assert axis_bin_indices(np.array([0.01, 0.125, 0.5, 0.999999])).tolist() == [0, 1, 4, 7]
