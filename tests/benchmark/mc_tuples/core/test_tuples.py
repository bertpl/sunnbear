"""`MCTuples` validates and stores a tuple set, maps it onto a test function, and reports its spread."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesStats
from sunnbear._core.benchmark.mc_tuples.core import GPQ_LEVEL
from sunnbear._core.stats import gpq

# The diagonal set has 8 tuples, evenly spaced on each axis: u rises and v falls, so neighbors are diagonal at L2
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
def test_stats_reports_min_separations_and_their_fractions():
    """Evenly spaced tuples give separations 1/8 per axis and √2/8 in L2, and their fractions."""
    # --- act --------------------------
    stats = MCTuples(_DIAGONAL_U, _DIAGONAL_V).stats()

    # --- assert -----------------------
    assert stats.size == 8
    assert stats.min_separation_u == pytest.approx(1 / 8)
    assert stats.min_separation_v == pytest.approx(1 / 8)
    assert stats.min_separation_l2 == pytest.approx(np.sqrt(2) / 8)
    assert stats.min_separation_u_fraction == pytest.approx(7 / 8)
    assert stats.min_separation_v_fraction == pytest.approx(7 / 8)
    assert stats.min_separation_l2_fraction == pytest.approx(np.sqrt(2) / 8 * (np.sqrt(8) - 1))


def test_stats_describe_tuples_on_the_edges_of_the_unit_square():
    """`MCTuplesStats` reports the size and the min separations of tuples on the edges of the unit square."""
    # --- act --------------------------
    stats = MCTuplesStats(np.array([[0.0, 0.0], [0.5, 1.0], [1.0, 0.5]]))

    # --- assert -----------------------
    assert stats.size == 3
    assert stats.min_separation_u == pytest.approx(0.5)
    assert stats.min_separation_v == pytest.approx(0.5)
    assert stats.min_separation_l2 == pytest.approx(np.sqrt(0.5))


def test_stats_reports_gpq_fractions_and_the_score_for_evenly_spaced_tuples():
    """With every separation equal, each gpq(0.1) equals it, so the gpq fractions equal the min separation fractions."""
    # --- act --------------------------
    stats = MCTuples(_DIAGONAL_U, _DIAGONAL_V).stats()

    # --- assert -----------------------
    assert stats.gpq_u_fraction == pytest.approx(7 / 8)
    assert stats.gpq_v_fraction == pytest.approx(7 / 8)
    assert stats.gpq_l2_fraction == pytest.approx(np.sqrt(2) / 8 * (np.sqrt(8) - 1))
    assert stats.score == pytest.approx((7 / 8 * 7 / 8 * stats.gpq_l2_fraction**2) ** 0.25)


def test_stats_takes_gpq_over_each_tuple_s_nearest_neighbor_separation():
    """Along u, the values 0.1, 0.2, 0.5 and 0.9 have the nearest-neighbor separations 0.1, 0.1, 0.3 and 0.4."""
    # --- arrange ----------------------
    stats = MCTuplesStats(np.array([[0.5, 0.1], [0.1, 0.2], [0.9, 0.3], [0.2, 0.4]]))

    # --- act / assert -----------------
    assert stats.gpq_u_fraction == pytest.approx(gpq([0.3, 0.1, 0.4, 0.1], GPQ_LEVEL) * 3)
    assert stats.min_separation_u == pytest.approx(0.1)


def test_extended_by_appends_the_other_set_s_tuples():
    """`extended_by` returns this set's tuples followed by the other set's, in order."""
    # --- act --------------------------
    extended = MCTuples([0.1, 0.2], [0.3, 0.4]).extended_by(MCTuples([0.5, 0.6], [0.7, 0.8]))

    # --- assert -----------------------
    assert extended.u.tolist() == [0.1, 0.2, 0.5, 0.6]
    assert extended.v.tolist() == [0.3, 0.4, 0.7, 0.8]
