"""`MCTuplesSelectionSolve` draws its population in the free lower-half LHS lanes and tiles, builds its constraints and
a valid random start, and refuses a selection that breaks them."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesConstructionError, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.rotations import tuple_array_of
from sunnbear._core.benchmark.mc_tuples.construction.selection import MCTuplesSelectionSolve
from sunnbear._core.benchmark.mc_tuples.construction.solve import INCLUSION_CONSTRAINT_WEIGHT, MCTuplesSolveSettings

# The smallest size's only base tuple: u in LHS lane 1 of size 16 and v in LHS lane 4, so in tile 1 of size 16 (tile
# column 0, tile row 1). It leaves free the lanes 0, 2, 3, 5, 6 and 7 and the tiles 0, 4 and 5 of [0, 0.5]^2.
_BASE_4 = np.array([[0.1, 0.3]])


def _solve(size: MCTuplesSize, required_base_tuple_array: np.ndarray, n_population: int) -> MCTuplesSelectionSolve:
    """Return the solve of `size` on `required_base_tuple_array`, with `n_population` candidates drawn."""
    settings = MCTuplesSolveSettings(n_workers=1, seed=42, rng=np.random.default_rng(5))
    return MCTuplesSelectionSolve(n_population, required_base_tuple_array, size, settings)


def _base_tuples_up_to(size: MCTuplesSize) -> np.ndarray:
    """Return the base tuples of `size` and every size below it, each size built from its random starting selection
    on a small population, without running max-div."""
    base_tuple_array = np.zeros((0, 2))
    for each_size in MCTuplesSize.up_to(size):
        solve = _solve(each_size, base_tuple_array, n_population=2**10)
        new = solve.population.base_tuple_array[solve._initial_new_selection()]
        base_tuple_array = np.vstack([base_tuple_array, new])
    return base_tuple_array


# ==================================================================================================
#  Free lanes and tiles, population and constraints
# ==================================================================================================
def test_the_population_lies_only_in_the_lanes_and_tiles_that_the_size_below_leaves_free():
    """At size 16, the LHS lanes and the tile of the size below's base tuple are not free, and no candidate lies in
    them."""
    # --- act --------------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)

    # --- assert -----------------------
    assert solve.free_lanes.tolist() == [0, 2, 3, 5, 6, 7]
    assert solve.free_tiles.tolist() == [0, 4, 5]
    u, v = solve.population.u, solve.population.v
    for values in (u, v):
        assert np.isin(MCTuplesSize.SIZE_16.lhs_lane_indices(values), solve.free_lanes).all()
    assert np.isin(MCTuplesSize.SIZE_16.tile_indices(u, v), solve.free_tiles).all()


def test_constraints_allow_1_new_value_per_free_lane_require_1_new_base_tuple_per_free_tile_and_keep_the_size_below():
    """Size 16 gets 1 constraint per free lane that allows at most 1 candidate with its u or its v in that lane, 1 per
    free tile that requires exactly 1 candidate in that tile, and the weighted constraint that keeps the dummy
    rotational sibling tuple and the only base tuple of the size below."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)
    u, v = solve.population.u, solve.population.v

    # --- act --------------------------
    constraints = solve._constraints()

    # --- assert -----------------------
    lane_constraints, tile_constraints, inclusion = constraints[:6], constraints[6:9], constraints[9]
    assert len(constraints) == 6 + 3 + 1
    assert all(c.min_count == 0 and c.max_count == 1 for c in lane_constraints)
    in_lane_0 = np.flatnonzero(
        (MCTuplesSize.SIZE_16.lhs_lane_indices(u) == 0) | (MCTuplesSize.SIZE_16.lhs_lane_indices(v) == 0)
    )
    assert lane_constraints[0].int_set == set((2 + in_lane_0).tolist())
    assert all(c.min_count == c.max_count == 1 for c in tile_constraints)
    in_tile_0 = np.flatnonzero(MCTuplesSize.SIZE_16.tile_indices(u, v) == 0)
    assert tile_constraints[0].int_set == set((2 + in_tile_0).tolist())
    assert inclusion.int_set == set(range(2))
    assert inclusion.min_count == inclusion.max_count == 2
    assert inclusion.weight == INCLUSION_CONSTRAINT_WEIGHT


# ==================================================================================================
#  Random starting selection
# ==================================================================================================
@pytest.mark.parametrize("size", [MCTuplesSize.SIZE_4, MCTuplesSize.SIZE_16, MCTuplesSize.SIZE_1024])
def test_the_assignment_gives_each_free_tile_a_lane_of_its_tile_column_and_one_of_its_tile_row(size):
    """Every free lane goes to exactly 1 free tile, as its u lane or its v lane, and each tile's u lane lies in its tile
    column and its v lane in its tile row."""
    # --- arrange ----------------------
    if size.size_below is None:
        required_base_tuple_array = np.zeros((0, 2))
    else:
        required_base_tuple_array = _base_tuples_up_to(size.size_below)
    solve = _solve(size, required_base_tuple_array, n_population=16)

    # --- act --------------------------
    u_lanes, v_lanes = solve._assign_lhs_lanes_to_tiles(
        solve.free_lanes, solve.free_tiles, size, np.random.default_rng(9)
    )

    # --- assert -----------------------
    assert np.sort(np.concatenate([u_lanes, v_lanes])).tolist() == solve.free_lanes.tolist()
    lane_centers = (np.concatenate([u_lanes, v_lanes]) + 0.5) / int(size)
    u_centers, v_centers = lane_centers[: u_lanes.size], lane_centers[u_lanes.size :]
    assert size.tile_indices(u_centers, v_centers).tolist() == solve.free_tiles.tolist()


@pytest.mark.parametrize(
    "size, n_population",
    [
        (MCTuplesSize.SIZE_4, 8192),
        (MCTuplesSize.SIZE_64, 8192),
        (MCTuplesSize.SIZE_1024, 8192),  # about 1 candidate per 18 LHS cells: most cells take a new candidate
        (MCTuplesSize.SIZE_64, 1),  # every needed cell takes a new candidate
    ],
)
def test_the_random_starting_selection_fills_every_free_lane_and_free_tile_of_the_size(size, n_population):
    """The starting selection holds as many candidates as the size has new base tuples, ascending, and with the size
    below's base tuples it holds exactly 1 tuple in each LHS lane and tile of the size, however few candidates the
    population drew."""
    # --- arrange ----------------------
    if size.size_below is None:
        required_base_tuple_array = np.zeros((0, 2))
    else:
        required_base_tuple_array = _base_tuples_up_to(size.size_below)

    # --- act --------------------------
    solve = _solve(size, required_base_tuple_array, n_population)
    start = solve._initial_new_selection()

    # --- assert -----------------------
    assert start.size == size.n_new // 4
    assert np.array_equal(start, np.sort(start))
    base_tuple_array = np.vstack([required_base_tuple_array, solve.population.base_tuple_array[start]])
    size.check_lhs_lanes_and_tiles(tuple_array_of(base_tuple_array))


def test_the_random_starting_selection_adds_no_candidate_where_the_population_holds_one():
    """At size 16, 36 candidates, 1 per LHS cell of the 6 free lanes, leave 1 candidate in each of the 21 off-diagonal
    cells of the free tiles, so the starting selection adds no candidate.

    The other 9 off-diagonal cells lie in the size below's tile: u in lane 0, 2 or 3, and v in lane 5, 6 or 7.
    """
    # --- act --------------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=6 * 6)

    # --- assert -----------------------
    assert solve.population.u.size == 30 - 9


# ==================================================================================================
#  Validation
# ==================================================================================================
def test_validation_returns_a_valid_selection_s_new_candidates():
    """The starting selection of size 16, with the dummy rotational sibling tuple and the size below's base tuple,
    meets the constraints, and `_validated_new_selection` returns its new candidates unchanged."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)
    new = solve._initial_new_selection()

    # --- act / assert -----------------
    assert solve._validated_new_selection(np.concatenate([[0, 1], 2 + new])).tolist() == new.tolist()


def test_validation_refuses_a_selection_without_the_dummy_rotational_sibling_tuple():
    """A size-16 selection that leaves out the dummy rotational sibling tuple, index 0, raises an error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)

    # --- act / assert -----------------
    with pytest.raises(
        MCTuplesConstructionError, match="1 of the dummy rotational sibling tuple and the size below's base tuples"
    ):
        solve._validated_new_selection(np.arange(1, 6))


def test_validation_refuses_a_selection_that_leaves_an_lhs_lane_without_exactly_1_tuple():
    """A size-16 selection that swaps 1 candidate of the starting selection for another candidate in the same tile and
    v lane, but in another u lane, raises an error that names the size and the LHS lanes along u."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)
    new = solve._initial_new_selection().copy()
    u, v = solve.population.u, solve.population.v
    lhs_lane_indices = MCTuplesSize.SIZE_16.lhs_lane_indices
    tiles = MCTuplesSize.SIZE_16.tile_indices(u, v)
    is_in_same_tile_and_v_lane = (tiles == tiles[new[0]]) & (lhs_lane_indices(v) == lhs_lane_indices(v)[new[0]])
    new[0] = np.flatnonzero(is_in_same_tile_and_v_lane & (lhs_lane_indices(u) != lhs_lane_indices(u)[new[0]]))[0]

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="Size 16: LHS lanes along u that do not hold exactly 1 tuple"):
        solve._validated_new_selection(np.concatenate([[0, 1], 2 + np.sort(new)]))
