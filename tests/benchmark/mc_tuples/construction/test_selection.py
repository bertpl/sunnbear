"""`MCTuplesSelectionSolve` draws its population in the free lower fine lanes, builds its constraints and a valid random
start, and refuses a selection that breaks them."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, MCTuplesConstructionError, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.rotations import N_LOWER_FINE_LANES
from sunnbear._core.benchmark.mc_tuples.construction.selection import MCTuplesSelectionSolve
from sunnbear._core.benchmark.mc_tuples.construction.solve import INCLUSION_CONSTRAINT_WEIGHT, MCTuplesSolveSettings

# The 8 base tuples of the smallest size lie in 16 lower fine lanes, 32 apart: u in the even ones, v in the odd ones.
_LANES_32 = 5 + 32 * np.arange(16)
_BASE_32 = np.column_stack([_LANES_32[0::2] + 0.5, _LANES_32[1::2] + 0.25]) / N_FINE_LANES


def _solve(size: MCTuplesSize, required_base_tuple_array: np.ndarray, n_population: int) -> MCTuplesSelectionSolve:
    """Return the solve of `size` on `required_base_tuple_array`, with `n_population` candidates drawn."""
    settings = MCTuplesSolveSettings(n_workers=1, seed=42, rng=np.random.default_rng(5))
    return MCTuplesSelectionSolve(n_population, required_base_tuple_array, size, settings)


def _distinct_lane_selection(solve: MCTuplesSelectionSolve, n: int) -> np.ndarray:
    """Return `n` candidates, as indices into the population, whose `2 n` lower fine lanes are distinct, each the first
    candidate in population order whose 2 lanes are both unused."""
    picked, used = [], set()
    for i in range(solve.population.u.size):
        lanes = {int(solve.population.u_lane[i]), int(solve.population.v_lane[i])}
        if not lanes & used:
            picked.append(i)
            used |= lanes
        if len(picked) == n:
            break
    return np.array(picked)


# ==================================================================================================
#  Population and constraints
# ==================================================================================================
def test_the_population_lies_only_in_the_lower_fine_lanes_that_the_size_below_leaves_free():
    """The 16 lanes of the size below's base tuples are not free, and no candidate lies in them."""
    # --- act --------------------------
    solve = _solve(MCTuplesSize.SIZE_64, _BASE_32, n_population=8192)

    # --- assert -----------------------
    assert solve.free_lanes.tolist() == np.setdiff1d(np.arange(N_LOWER_FINE_LANES), _LANES_32).tolist()
    for lanes in (solve.population.u_lane, solve.population.v_lane):
        assert np.isin(lanes, solve.free_lanes).all()


def test_constraints_allow_at_most_1_new_value_per_free_lane_and_keep_the_placeholder_and_the_size_below():
    """Size 64 gets 1 at-most-1 constraint per free lane, over every candidate with its u or its v in that lane, and
    the weighted constraint that keeps the placeholder and the 8 base tuples of the size below."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_64, _BASE_32, n_population=8192)
    population = solve.population

    # --- act --------------------------
    constraints = solve._constraints()

    # --- assert -----------------------
    lane_constraints, inclusion = constraints[:-1], constraints[-1]
    assert len(lane_constraints) == solve.free_lanes.size
    assert all(c.min_count == 0 and c.max_count == 1 for c in lane_constraints)
    lane = solve.free_lanes[0]
    in_lane = np.flatnonzero((population.u_lane == lane) | (population.v_lane == lane))
    assert set((9 + in_lane).tolist()) in [c.int_set for c in lane_constraints]
    assert inclusion.int_set == set(range(9))
    assert inclusion.min_count == inclusion.max_count == 9
    assert inclusion.weight == INCLUSION_CONSTRAINT_WEIGHT


# ==================================================================================================
#  Random starting selection
# ==================================================================================================
@pytest.mark.parametrize(
    "size, required_base_tuple_array",
    [(MCTuplesSize.SIZE_32, np.zeros((0, 2))), (MCTuplesSize.SIZE_64, _BASE_32)],
)
def test_the_random_starting_selection_holds_the_new_base_tuples_in_distinct_lanes(size, required_base_tuple_array):
    """The starting selection holds as many candidates as the size has new base tuples, ascending, with their 16
    values in 16 distinct lower fine lanes."""
    # --- arrange ----------------------
    solve = _solve(size, required_base_tuple_array, n_population=8192)

    # --- act --------------------------
    start = solve._initial_new_selection()

    # --- assert -----------------------
    assert start.size == 8
    assert np.array_equal(start, np.sort(start))
    assert np.unique(np.concatenate([solve.population.u_lane[start], solve.population.v_lane[start]])).size == 16


def test_the_random_starting_selection_of_the_largest_size_uses_every_free_lane():
    """At size 1024, the 128 new base tuples fill the 256 free lanes, when every off-diagonal fine cell of the free
    lanes holds a candidate."""
    # --- arrange ----------------------
    lanes = np.random.default_rng(6).permutation(N_LOWER_FINE_LANES)[:256]
    required_base_tuple_array = np.column_stack([lanes[0::2] + 0.5, lanes[1::2] + 0.5]) / N_FINE_LANES
    solve = _solve(MCTuplesSize.SIZE_1024, required_base_tuple_array, n_population=256 * 256)

    # --- act --------------------------
    start = solve._initial_new_selection()

    # --- assert -----------------------
    new_lanes = np.concatenate([solve.population.u_lane[start], solve.population.v_lane[start]])
    assert np.sort(new_lanes).tolist() == solve.free_lanes.tolist()


def test_the_random_starting_selection_needs_enough_candidates():
    """A population of 4 candidates holds at most 4 new base tuples, too few for the 8 of size 32, and raises an
    error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_32, np.zeros((0, 2)), n_population=4)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="candidates with unused lanes, for 8 new base tuples"):
        solve._initial_new_selection()


# ==================================================================================================
#  Validation
# ==================================================================================================
def test_validation_returns_a_valid_selection_s_new_candidates():
    """A selection of the placeholder and 8 candidates in distinct lanes meets the smallest size's constraints, and its
    new candidates come back as they are."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_32, np.zeros((0, 2)), n_population=8192)
    new = np.sort(_distinct_lane_selection(solve, 8))

    # --- act / assert -----------------
    assert solve._validated_new_selection(np.concatenate([[0], 1 + new])).tolist() == new.tolist()


def test_validation_refuses_a_selection_without_the_placeholder():
    """A size-64 selection that leaves out the placeholder, index 0, raises an error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_64, _BASE_32, n_population=8192)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="1 of the placeholder and the size below's base tuples"):
        solve._validated_new_selection(np.arange(1, 18))


def test_validation_refuses_2_new_values_in_1_lane():
    """7 candidates in distinct lanes and an 8th that shares a lane with the first raise an error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_32, np.zeros((0, 2)), n_population=8192)
    new = _distinct_lane_selection(solve, 7)
    u_lanes, v_lanes = solve.population.u_lane, solve.population.v_lane
    shares_a_lane = np.flatnonzero((u_lanes == u_lanes[new[0]]) | (v_lanes == u_lanes[new[0]]))
    new = np.sort(np.append(new, shares_a_lane[shares_a_lane != new[0]][0]))

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="a lower fine lane holds 2 or more new values"):
        solve._validated_new_selection(np.concatenate([[0], 1 + new]))
