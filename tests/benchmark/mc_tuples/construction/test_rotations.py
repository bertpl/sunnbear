"""The 4 tuples of each base tuple give every size the same u values and v values, symmetric around 0.5."""

import math

import numpy as np

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, fine_lanes_of
from sunnbear._core.benchmark.mc_tuples.construction.rotations import N_LOWER_FINE_LANES
from sunnbear._core.benchmark.mc_tuples.construction.size_result import MCTuplesSizeResult


def test_the_4_tuples_of_each_base_tuple_give_equal_axes_with_means_of_0_5_and_1_tuple_per_fine_lane():
    """Built from 256 base tuples in distinct lower fine lanes, each group of 4 tuples starts with its base tuple, and
    every prefix of whole groups of 4 tuples has:

    - the same u values and v values, bit for bit;
    - means of exactly 0.5;
    - at most 1 tuple per fine lane on each axis.
    """
    # --- arrange ----------------------
    rng = np.random.default_rng(0)
    lanes = rng.permutation(N_LOWER_FINE_LANES).reshape(2, -1)
    base_tuple_array = ((lanes + rng.random(lanes.shape)) / (2 * N_LOWER_FINE_LANES)).T

    # --- act --------------------------
    tuple_array = MCTuplesSizeResult._tuple_array_of(base_tuple_array)

    # --- assert -----------------------
    assert np.array_equal(tuple_array[0::4], base_tuple_array)
    for size in MCTuplesSize:
        u, v = tuple_array[:size, 0], tuple_array[:size, 1]
        assert np.array_equal(np.sort(u), np.sort(v))
        assert math.fsum(u) / size == 0.5
        assert np.bincount(fine_lanes_of(u)).max() == 1


def test_a_base_tuple_in_a_diagonal_cell_puts_2_tuples_in_1_fine_lane():
    """A base tuple whose u and v share fine lane 100 puts its 4 tuples in fine u-lanes 100, 923, 923 and 100."""
    # --- act --------------------------
    tuple_array = MCTuplesSizeResult._tuple_array_of(np.array([[100.3, 100.7]]) / 1024)

    # --- assert -----------------------
    assert fine_lanes_of(tuple_array[:, 0]).tolist() == [100, 923, 923, 100]
