"""The 4 tuples of each base tuple give every size the same u values and v values, symmetric around 0.5."""

import math

import numpy as np

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.rotations import tuple_array_of

_LARGEST_SIZE = max(MCTuplesSize)


def test_the_4_tuples_of_each_base_tuple_give_equal_axes_with_means_of_0_5_and_1_tuple_per_lhs_lane():
    """Built from 256 base tuples in distinct lower-half LHS lanes of the largest size, each group of 4 tuples starts
    with its base tuple, and every prefix of whole groups of 4 tuples has:

    - the same u values and v values, bit for bit;
    - means of exactly 0.5;
    - at most 1 tuple per LHS lane of the largest size on each axis.
    """
    # --- arrange ----------------------
    rng = np.random.default_rng(0)
    lanes = rng.permutation(_LARGEST_SIZE.n_lower_half_lhs_lanes).reshape(2, -1)
    base_tuple_array = ((lanes + rng.random(lanes.shape)) / int(_LARGEST_SIZE)).T

    # --- act --------------------------
    tuple_array = tuple_array_of(base_tuple_array)

    # --- assert -----------------------
    assert np.array_equal(tuple_array[0::4], base_tuple_array)
    for size in MCTuplesSize:
        u, v = tuple_array[:size, 0], tuple_array[:size, 1]
        assert np.array_equal(np.sort(u), np.sort(v))
        assert math.fsum(u) / size == 0.5
        assert np.bincount(_LARGEST_SIZE.lhs_lane_indices(u)).max() == 1


def test_a_base_tuple_in_a_diagonal_cell_puts_2_tuples_in_1_lhs_lane():
    """A base tuple whose u and v share LHS lane 100 of the largest size puts its 4 tuples in its LHS lanes 100, 923,
    923 and 100 along u."""
    # --- act --------------------------
    tuple_array = tuple_array_of(np.array([[100.3, 100.7]]) / 1024)

    # --- assert -----------------------
    assert _LARGEST_SIZE.lhs_lane_indices(tuple_array[:, 0]).tolist() == [100, 923, 923, 100]
