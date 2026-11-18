"""`MCTuplesSize` lists the sizes of the shipped set and the sizes up to a given one, and splits each size into the size
below and its new tuples."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize


@pytest.mark.parametrize(
    "max_size, sizes",
    [
        (MCTuplesSize.SIZE_4, (4,)),
        (16, (4, 16)),  # a plain int is accepted
        (MCTuplesSize.SIZE_1024, tuple(MCTuplesSize)),
    ],
)
def test_up_to_lists_every_size_up_to_max_size(max_size, sizes):
    """`up_to` returns every size up to `max_size`, the smallest first, for a member or a plain int."""
    # --- act / assert -----------------
    assert MCTuplesSize.up_to(max_size) == sizes


def test_up_to_rejects_a_size_outside_the_set():
    """`up_to` raises a `ValueError` naming the sizes for an int that is not 1 of them."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="must be one of"):
        MCTuplesSize.up_to(100)


@pytest.mark.parametrize(
    "size, n_required, n_new",
    [
        (MCTuplesSize.SIZE_4, 0, 4),  # the smallest size has no size below
        (MCTuplesSize.SIZE_64, 16, 48),
        (MCTuplesSize.SIZE_1024, 256, 768),
    ],
)
def test_n_required_and_n_new_split_a_size_into_the_size_below_and_its_new_tuples(size, n_required, n_new):
    """A size takes `n_required` tuples from the size below and adds `n_new` new ones."""
    # --- act / assert -----------------
    assert (size.n_required, size.n_new) == (n_required, n_new)


# ==================================================================================================
#  LHS lanes and tiles
# ==================================================================================================
@pytest.mark.parametrize(
    "size, values, lane_indices",
    [
        (MCTuplesSize.SIZE_4, [0.01, 0.25, 0.49, 0.99], [0, 1, 1, 3]),
        (MCTuplesSize.SIZE_1024, [0.5 / 1024, 1 / 1024, 1023.5 / 1024], [0, 1, 1023]),
    ],
)
def test_lhs_lane_indices_puts_each_value_in_its_lane_of_width_1_over_size(size, values, lane_indices):
    """LHS lane `i` of a size holds the values in `[i, i + 1) / size`, its lower edge included."""
    # --- act / assert -----------------
    assert size.lhs_lane_indices(np.array(values)).tolist() == lane_indices


def test_lhs_lane_edges_bound_the_values_that_lhs_lane_indices_puts_in_each_lane():
    """The edges of LHS lanes 0, 5 and 15 of size 16 are their multiples of 1/16, and a value between a lane's edges
    lies in that lane."""
    # --- act --------------------------
    lows, highs = MCTuplesSize.SIZE_16.lhs_lane_edges(np.array([0, 5, 15]))

    # --- assert -----------------------
    assert (lows * 16).tolist() == [0, 5, 15]
    assert (highs * 16).tolist() == [1, 6, 16]
    assert MCTuplesSize.SIZE_16.lhs_lane_indices((lows + highs) / 2).tolist() == [0, 5, 15]


@pytest.mark.parametrize(
    "size, n_lower_half_lhs_lanes, n_tiles_per_axis",
    [(MCTuplesSize.SIZE_4, 2, 2), (MCTuplesSize.SIZE_64, 32, 8), (MCTuplesSize.SIZE_1024, 512, 32)],
)
def test_a_size_has_half_its_lhs_lanes_in_the_lower_half_and_sqrt_size_tiles_per_axis(
    size, n_lower_half_lhs_lanes, n_tiles_per_axis
):
    """A size of `n` tuples has `n / 2` LHS lanes in [0, 0.5] and `sqrt(n)` tiles per axis."""
    # --- act / assert -----------------
    assert (size.n_lower_half_lhs_lanes, size.n_tiles_per_axis) == (n_lower_half_lhs_lanes, n_tiles_per_axis)


def test_tile_indices_numbers_each_tile_by_its_column_and_row():
    """At size 16, with 4 tiles per axis, the tile in tile column 1 and tile row 3 is tile 1 * 4 + 3 = 7."""
    # --- act / assert -----------------
    assert MCTuplesSize.SIZE_16.tile_indices(np.array([0.01, 0.3, 0.99]), np.array([0.01, 0.8, 0.26])).tolist() == [
        0,
        7,
        13,
    ]


@pytest.mark.parametrize(
    "size, lower_half_tile_indices",
    [(MCTuplesSize.SIZE_4, [0]), (MCTuplesSize.SIZE_16, [0, 1, 4, 5])],
)
def test_lower_half_tile_indices_lists_the_tiles_in_the_lower_left_quarter(size, lower_half_tile_indices):
    """The tiles in [0, 0.5]^2 are those whose tile column and tile row both lie in the lower half."""
    # --- act / assert -----------------
    assert size.lower_half_tile_indices.tolist() == lower_half_tile_indices


def test_tile_columns_and_rows_inverts_tile_indices():
    """At size 64, the tile column and the tile row of each of the 64 tiles number it back to the same index."""
    # --- arrange ----------------------
    size = MCTuplesSize.SIZE_64
    centers = (np.arange(8) + 0.5) / 8
    u, v = np.meshgrid(centers, centers, indexing="ij")

    # --- act --------------------------
    columns, rows = size.tile_columns_and_rows(size.tile_indices(u.ravel(), v.ravel()))

    # --- assert -----------------------
    assert columns.tolist() == np.repeat(np.arange(8), 8).tolist()
    assert rows.tolist() == np.tile(np.arange(8), 8).tolist()


def test_tile_columns_of_lhs_lanes_gives_the_tile_column_under_which_each_lhs_lane_lies():
    """At size 16, each tile spans 4 LHS lanes per axis, so LHS lanes 0 to 3 lie under tile column 0, 4 to 7 under 1."""
    # --- act / assert -----------------
    assert MCTuplesSize.SIZE_16.tile_columns_of_lhs_lanes(np.array([0, 3, 4, 7, 15])).tolist() == [0, 0, 1, 1, 3]


def _grid_tuple_array(size: MCTuplesSize) -> np.ndarray:
    """Return `size` tuples that hold exactly 1 tuple in each LHS lane and each tile of `size`.

    The tuple in tile column `c` and tile row `r` lies in LHS lane `c * k + r` along u and `r * k + c` along v, with
    `k = sqrt(size)`, at the lane's center.
    """
    k = size.n_tiles_per_axis
    columns, rows = np.divmod(np.arange(int(size)), k)
    return np.column_stack([columns * k + rows + 0.5, rows * k + columns + 0.5]) / int(size)


@pytest.mark.parametrize("size", MCTuplesSize)
def test_check_lhs_lanes_and_tiles_accepts_1_tuple_per_lhs_lane_and_per_tile(size):
    """A grid of tuples with exactly 1 tuple in each LHS lane, along u and along v, and in each tile passes."""
    # --- act / assert -----------------
    size.check_lhs_lanes_and_tiles(_grid_tuple_array(size))


def _swap_u_of_tuples_0_and_5(tuple_array: np.ndarray) -> np.ndarray:
    """Return the size-16 grid with the u values of its tuples in tiles (0, 0) and (1, 1) swapped, which moves them
    into tiles (1, 0) and (0, 1), where other tuples already lie; every LHS lane keeps 1 tuple."""
    tuple_array[[0, 5], 0] = tuple_array[[5, 0], 0]
    return tuple_array


def _move_tuple_0_into_the_lhs_lanes_of_tuple_1(axis: int):
    """Return a function that gives tuple 0 the value of tuple 1 along `axis`, 0 for u and 1 for v."""

    def move(tuple_array: np.ndarray) -> np.ndarray:
        """Give tuple 0 the value of tuple 1 along the axis."""
        tuple_array[0, axis] = tuple_array[1, axis]
        return tuple_array

    return move


@pytest.mark.parametrize(
    "change, message",
    [
        (_swap_u_of_tuples_0_and_5, "Tiles that do not hold exactly 1 tuple: 4 of 16"),
        (_move_tuple_0_into_the_lhs_lanes_of_tuple_1(0), "LHS lanes along u that do not hold exactly 1 tuple: 2 of 16"),
        (_move_tuple_0_into_the_lhs_lanes_of_tuple_1(1), "LHS lanes along v that do not hold exactly 1 tuple: 2 of 16"),
        (
            lambda tuple_array: tuple_array[1:],
            "LHS lanes along u that do not hold exactly 1 tuple: 1 of 16",
        ),  # tuple 0 is dropped
    ],
)
def test_check_lhs_lanes_and_tiles_refuses_an_lhs_lane_or_a_tile_without_exactly_1_tuple(change, message):
    """At size 16, a grid of tuples with 1 tuple moved or dropped, or 2 swapped between tiles, raises a `ValueError`
    that counts the parts of the first kind that break, checked in the order LHS lanes along u, along v, tiles."""
    # --- arrange ----------------------
    tuple_array = change(_grid_tuple_array(MCTuplesSize.SIZE_16))

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        MCTuplesSize.SIZE_16.check_lhs_lanes_and_tiles(tuple_array)
