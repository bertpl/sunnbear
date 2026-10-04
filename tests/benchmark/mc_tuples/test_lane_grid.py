"""`LaneGrid` assigns the new values to the gaps, cuts the lanes, numbers the cells, and checks 1 tuple per lane."""

import itertools

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.benchmark.mc_tuples.lane_grid import LaneGrid

# A size-4 set with 1 tuple per lane on each axis; the tests use it as the size below size 8.
_SIZE_4 = MCTuples([0.1, 0.4, 0.6, 0.9], [0.9, 0.1, 0.6, 0.4])


def _min_gap(old_values: list[float], new_values: np.ndarray) -> float:
    """Return the smallest gap between consecutive values of the axis, old and new together."""
    return float(np.diff(np.sort(np.concatenate([old_values, new_values]))).min())


def _one_tuple_per_random_cell(grid: LaneGrid, rng: np.random.Generator) -> MCTuples:
    """Return 1 random tuple inside each of random cells that pair each new u lane with a different new v lane."""
    samples = grid.sample_in_cells(grid.random_one_per_new_lane_cells(rng), 1, rng)[:, 0, :]
    return MCTuples(samples[:, 0], samples[:, 1])


def _best_min_gap_by_brute_force(old_values: list[float], n_new: int) -> float:
    """Return the largest min gap over every assignment of `n_new` values to the gaps between `old_values`.

    Within a gap, the values are spaced as `assign_new_values` spaces them, which is the best spacing for a
    given count; only the counts per gap are enumerated.
    """
    bounds = np.array([0.0, *sorted(old_values), 1.0])
    best = 0.0
    for counts in itertools.product(range(n_new + 1), repeat=bounds.size - 1):
        if sum(counts) == n_new:
            values = LaneGrid.space_values_in_gaps(bounds, np.array(counts))
            best = max(best, _min_gap(old_values, values))
    return best


# ==================================================================================================
#  New values and lanes of 1 axis
# ==================================================================================================
@pytest.mark.parametrize(
    "old_values, size, new_values",
    [
        ([], 4, [0.0, 1 / 3, 2 / 3, 1.0]),  # no old values: `i / (size - 1)`, from 0 to 1
        ([0.1, 0.9], 6, [0.26, 0.42, 0.58, 0.74]),  # an interior gap: 5 equal sub-gaps between 0.1 and 0.9
        ([0.5], 5, [0.0, 0.25, 0.75, 1.0]),  # 2 edge gaps: the outermost values at 0 and 1
    ],
)
def test_assign_new_values_spaces_the_values_evenly_within_each_gap(old_values, size, new_values):
    """The new values are evenly spaced within each gap, and an edge gap puts its outermost value at 0 or 1."""
    # --- act / assert -----------------
    assert LaneGrid.assign_new_values(np.array(old_values), size).tolist() == pytest.approx(new_values)


@pytest.mark.parametrize(
    "old_values, n_new",
    [
        ([0.5], 3),
        ([0.3, 0.35, 0.9], 3),
        ([0.1, 0.2, 0.6, 0.65], 4),
        ([0.02, 0.5, 0.98], 5),
    ],
)
def test_the_greedy_assignment_maximizes_the_smallest_gap(old_values, n_new):
    """On small cases, `assign_new_values` maximizes the smallest gap over every assignment of counts to the gaps."""
    # --- act --------------------------
    new_values = LaneGrid.assign_new_values(np.array(old_values), len(old_values) + n_new)

    # --- assert -----------------------
    assert new_values.size == n_new
    assert (np.diff(new_values) > 0).all()
    assert _min_gap(old_values, new_values) == pytest.approx(_best_min_gap_by_brute_force(old_values, n_new))


def test_lane_boundaries_are_0_the_midpoints_and_1():
    """The boundaries of 3 values are 0, the 2 midpoints between the sorted values, and 1."""
    # --- act / assert -----------------
    assert LaneGrid.lane_boundaries(np.array([0.8, 0.2, 0.4])).tolist() == pytest.approx([0.0, 0.3, 0.6, 1.0])


# ==================================================================================================
#  The grid of 1 size
# ==================================================================================================
def test_every_new_value_lies_in_its_own_lane_and_no_old_value_inside_a_new_lane():
    """At size 8, each new value sits inside its lane, the new lanes do not overlap, and no old value is inside one."""
    # --- act --------------------------
    grid = LaneGrid.for_size(8, _SIZE_4)

    # --- assert -----------------------
    assert grid.n_new == 4
    axes = ((grid.new_u_values, grid.new_u_lanes, _SIZE_4.u), (grid.new_v_values, grid.new_v_lanes, _SIZE_4.v))
    for values, lanes, old_values in axes:
        assert ((lanes[:, 0] <= values) & (values <= lanes[:, 1])).all()
        assert (lanes[:-1, 1] <= lanes[1:, 0]).all()
        assert not ((lanes[:, 0] < old_values[:, None]) & (old_values[:, None] < lanes[:, 1])).any()


def test_the_cells_are_numbered_row_by_row_and_represented_by_their_values():
    """Cell `i * n_new + j` is represented by the point `(new_u_values[i], new_v_values[j])`."""
    # --- act --------------------------
    grid = LaneGrid.for_size(8, _SIZE_4)

    # --- assert -----------------------
    assert grid.n_cells == 16
    u, v = grid.new_u_values, grid.new_v_values
    assert grid.cell_points[[0, 1, 4]].tolist() == [[u[0], v[0]], [u[0], v[1]], [u[1], v[0]]]
    assert grid.required_and_cell_points(np.array([1, 4])).tolist() == [
        *_SIZE_4.points.tolist(),
        [u[0], v[1]],
        [u[1], v[0]],
    ]
    assert [cells.tolist() for cells in grid.lane_cells()[:2]] == [[0, 1, 2, 3], [4, 5, 6, 7]]
    assert grid.lane_cells()[4].tolist() == [0, 4, 8, 12]


def test_random_cells_pair_each_new_u_lane_with_1_new_v_lane():
    """The random cells hold 1 cell per new u lane and 1 per new v lane."""
    # --- arrange ----------------------
    grid = LaneGrid.for_size(8, _SIZE_4)

    # --- act --------------------------
    cells = grid.random_one_per_new_lane_cells(np.random.default_rng(0))

    # --- assert -----------------------
    assert grid.is_one_per_new_lane(cells)
    assert not grid.is_one_per_new_lane(np.array([0, 1, 2, 3]))  # the 4 cells of the first new u lane


def test_samples_lie_strictly_inside_their_cells():
    """Every sample of a cell lies strictly between the cell's lane boundaries on both axes."""
    # --- arrange ----------------------
    grid = LaneGrid.for_size(8, _SIZE_4)
    cells = np.array([0, 5, 15])

    # --- act --------------------------
    samples = grid.sample_in_cells(cells, 50, np.random.default_rng(3))

    # --- assert -----------------------
    rows, columns = np.divmod(cells, grid.n_new)
    assert samples.shape == (3, 50, 2)
    assert (grid.new_u_lanes[rows, 0][:, None] < samples[:, :, 0]).all()
    assert (samples[:, :, 0] < grid.new_u_lanes[rows, 1][:, None]).all()
    assert (grid.new_v_lanes[columns, 0][:, None] < samples[:, :, 1]).all()
    assert (samples[:, :, 1] < grid.new_v_lanes[columns, 1][:, None]).all()


# ==================================================================================================
#  The check of a whole size
# ==================================================================================================
@pytest.mark.parametrize(
    "tuples, is_one_per_lane",
    [
        (_SIZE_4, True),
        (MCTuples([0.1, 0.4, 0.6, 0.7], [0.9, 0.1, 0.6, 0.4]), False),  # 0.6 and 0.7 share the third u lane
        (MCTuples([0.1, 0.4, 0.6, 0.9], [0.9, 0.95, 0.6, 0.4]), False),  # 0.9 and 0.95 share the last v lane
        (MCTuples([0.1, 0.4, 0.9], [0.9, 0.1, 0.4]), False),  # 3 tuples, not the 4 of the size
    ],
)
def test_is_one_per_lane_requires_exactly_1_tuple_per_lane_on_each_axis(tuples, is_one_per_lane):
    """At the smallest size, the lanes meet midway between `i / (size - 1)`; each must hold exactly 1 tuple."""
    # --- act / assert -----------------
    assert LaneGrid.for_size(4, None).is_one_per_lane(tuples) == is_one_per_lane


def test_a_nested_size_holds_1_per_lane_when_each_new_tuple_stays_inside_its_cell():
    """Size 8 built from size 4 and 1 sample per selected cell holds exactly 1 tuple per lane of size 8."""
    # --- arrange ----------------------
    rng = np.random.default_rng(5)
    grid = LaneGrid.for_size(8, _SIZE_4)
    new_tuples = _one_tuple_per_random_cell(grid, rng)

    # --- act --------------------------
    tuples = _SIZE_4.extended_by(new_tuples)

    # --- assert -----------------------
    assert grid.is_one_per_lane(tuples)
    assert not grid.is_one_per_lane(_SIZE_4.extended_by(_SIZE_4))


def test_is_one_per_lane_on_rebuilt_grid_checks_a_shipped_size_and_refuses_other_sizes():
    """A size-32 set with 1 sample per selected cell passes the check; a size outside `MCTuplesSize` is refused."""
    # --- arrange ----------------------
    rng = np.random.default_rng(6)
    tuples = _one_tuple_per_random_cell(LaneGrid.for_size(32, None), rng)

    # --- act / assert -----------------
    assert LaneGrid.is_one_per_lane_on_rebuilt_grid(tuples)
    with pytest.raises(ValueError, match="one of"):
        LaneGrid.is_one_per_lane_on_rebuilt_grid(_SIZE_4)
