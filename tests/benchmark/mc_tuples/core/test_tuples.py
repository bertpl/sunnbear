"""`MCTuples` validates and stores a tuple set, maps it onto a test problem, and reports its spread and the bits of
information of its values."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesBitStats, MCTuplesStats
from sunnbear._core.benchmark.mc_tuples.core import GPQ_LEVEL
from sunnbear._core.stats import gpq
from sunnbear._core.utils.float_bits import n_bits

# The diagonal set has 8 tuples with u rising and v falling, 1/8 apart on each axis, also across 0 and 1 from the last
# tuple to the first, so every tuple's nearest neighbors lie diagonally at the cyclic L2 distance sqrt(2)/8.
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
    """u = 0.5 lands at `xtol_min * sqrt(2)`, and v places c linearly between `c_min` and `c_max`."""
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
def test_stats_reports_min_separations_and_their_fractions():
    """Evenly spaced tuples give separations 1/8 per axis and sqrt(2)/8 in L2, so the fractions are 1 per axis, relative
    to 1/8, and 1/2 in L2, relative to the grid spacing 1/sqrt(8)."""
    # --- act --------------------------
    stats = MCTuples(_DIAGONAL_U, _DIAGONAL_V).stats()

    # --- assert -----------------------
    assert stats.size == 8
    assert stats.min_separation_u == pytest.approx(1 / 8)
    assert stats.min_separation_v == pytest.approx(1 / 8)
    assert stats.min_separation_l2 == pytest.approx(np.sqrt(2) / 8)
    assert stats.min_separation_u_fraction == pytest.approx(1.0)
    assert stats.min_separation_v_fraction == pytest.approx(1.0)
    assert stats.min_separation_l2_fraction == pytest.approx(0.5)


def test_stats_reports_gpq_fractions_and_the_score_for_evenly_spaced_tuples():
    """With every separation equal, each gpq(0.1) equals it, so the gpq fractions are 1, 1 and 1/2, and the score is
    (1*1*(1/2)^2)^(1/4) = sqrt(1/2)."""
    # --- act --------------------------
    stats = MCTuples(_DIAGONAL_U, _DIAGONAL_V).stats()

    # --- assert -----------------------
    assert stats.gpq_u_fraction == pytest.approx(1.0)
    assert stats.gpq_v_fraction == pytest.approx(1.0)
    assert stats.gpq_l2_fraction == pytest.approx(0.5)
    assert stats.score == pytest.approx(np.sqrt(0.5))


def test_stats_takes_gpq_over_each_tuple_s_nearest_neighbor_separation():
    """Along u, the values 0.1, 0.2, 0.5 and 0.9 have the cyclic nearest-neighbor separations 0.1, 0.1, 0.3 and 0.2,
    the last one across 0 and 1 to 0.1."""
    # --- arrange ----------------------
    stats = MCTuplesStats(np.array([[0.5, 0.1], [0.1, 0.2], [0.9, 0.3], [0.2, 0.4]]))

    # --- act / assert -----------------
    assert stats.gpq_u_fraction == pytest.approx(gpq([0.3, 0.1, 0.2, 0.1], GPQ_LEVEL) * 4)
    assert stats.min_separation_u == pytest.approx(0.1)


def test_stats_measures_the_l2_separation_along_the_shorter_arc_of_each_axis():
    """The tuples (0.05, 0.4) and (0.95, 0.7) lie 0.1 apart along u, across 0 and 1, 0.3 apart along v, and
    sqrt(0.1^2 + 0.3^2) apart in L2."""
    # --- arrange ----------------------
    stats = MCTuplesStats(np.array([[0.05, 0.4], [0.95, 0.7]]))

    # --- act / assert -----------------
    assert stats.min_separation_u == pytest.approx(0.1)
    assert stats.min_separation_v == pytest.approx(0.3)
    assert stats.min_separation_l2 == pytest.approx(np.sqrt(0.1**2 + 0.3**2))


def test_bit_stats_report_the_fewest_and_the_mean_bits_per_axis():
    """Per axis, `bit_stats` reports the fewest and the mean `n_bits` of the values."""
    # --- arrange ----------------------
    # The v values are e/10 and 1/sqrt(2) to 16 digits, so no short description reproduces them.
    u, v = [0.5, 1 / 3], [0.2718281828459045, 0.7071067811865476]

    # --- act --------------------------
    bit_stats = MCTuples(u, v).bit_stats()

    # --- assert -----------------------
    assert isinstance(bit_stats, MCTuplesBitStats)
    assert bit_stats.min_n_bits_u == pytest.approx(1.0)
    assert bit_stats.mean_n_bits_u == pytest.approx((1.0 + np.log2(3)) / 2)
    assert bit_stats.min_n_bits_v == pytest.approx(min(n_bits(x) for x in v))
    assert bit_stats.mean_n_bits_v == pytest.approx(np.mean([n_bits(x) for x in v]))
    assert bit_stats.min_n_bits_v > 45


def test_extended_by_appends_the_other_set_s_tuples():
    """`extended_by` returns this set's tuples followed by the other set's, in order."""
    # --- act --------------------------
    extended = MCTuples([0.1, 0.2], [0.3, 0.4]).extended_by(MCTuples([0.5, 0.6], [0.7, 0.8]))

    # --- assert -----------------------
    assert extended.u.tolist() == [0.1, 0.2, 0.5, 0.6]
    assert extended.v.tolist() == [0.3, 0.4, 0.7, 0.8]
