"""`MCTuplesSelectionSolve` draws its population in the free lower fine lanes, builds its constraints and a valid random
start, and refuses a selection that breaks them."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, MCTuplesConstructionError, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.rotations import N_LOWER_FINE_LANES
from sunnbear._core.benchmark.mc_tuples.construction.selection import MCTuplesSelectionSolve
from sunnbear._core.benchmark.mc_tuples.construction.solve import INCLUSION_CONSTRAINT_WEIGHT, MCTuplesSolveSettings

# The smallest size's only base tuple lies in 2 lower fine lanes, 32 apart: u in the first, v in the second.
_LANES_4 = 5 + 32 * np.arange(2)
_BASE_4 = np.column_stack([_LANES_4[0::2] + 0.5, _LANES_4[1::2] + 0.25]) / N_FINE_LANES


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
    """The 2 lanes of the size below's base tuple are not free, and no candidate lies in them."""
    # --- act --------------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)

    # --- assert -----------------------
    assert solve.free_lanes.tolist() == np.setdiff1d(np.arange(N_LOWER_FINE_LANES), _LANES_4).tolist()
    for lanes in (solve.population.u_lane, solve.population.v_lane):
        assert np.isin(lanes, solve.free_lanes).all()


def test_constraints_allow_1_new_value_per_free_lane_and_keep_the_dummy_rotational_sibling_tuple_and_the_size_below():
    """Size 16 gets 1 constraint per free lane that allows at most 1 candidate with its u or its v in that lane, and
    the weighted constraint that keeps the dummy rotational sibling tuple and the only base tuple of the size below."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)
    population = solve.population

    # --- act --------------------------
    constraints = solve._constraints()

    # --- assert -----------------------
    lane_constraints, inclusion = constraints[:-1], constraints[-1]
    assert len(lane_constraints) == solve.free_lanes.size
    assert all(c.min_count == 0 and c.max_count == 1 for c in lane_constraints)
    lane = solve.free_lanes[0]
    in_lane = np.flatnonzero((population.u_lane == lane) | (population.v_lane == lane))
    assert set((2 + in_lane).tolist()) in [c.int_set for c in lane_constraints]
    assert inclusion.int_set == set(range(2))
    assert inclusion.min_count == inclusion.max_count == 2
    assert inclusion.weight == INCLUSION_CONSTRAINT_WEIGHT


# ==================================================================================================
#  Random starting selection
# ==================================================================================================
@pytest.mark.parametrize(
    "size, required_base_tuple_array, n_new_base_tuples",
    [(MCTuplesSize.SIZE_4, np.zeros((0, 2)), 1), (MCTuplesSize.SIZE_16, _BASE_4, 3)],
)
def test_the_random_starting_selection_holds_the_new_base_tuples_in_distinct_lanes(
    size, required_base_tuple_array, n_new_base_tuples
):
    """The starting selection holds as many candidates as the size has new base tuples, ascending, and the u
    and v values of these candidates lie in distinct lower fine lanes, 1 lane per value."""
    # --- arrange ----------------------
    solve = _solve(size, required_base_tuple_array, n_population=8192)

    # --- act --------------------------
    start = solve._initial_new_selection()

    # --- assert -----------------------
    assert start.size == n_new_base_tuples
    assert np.array_equal(start, np.sort(start))
    lanes = np.concatenate([solve.population.u_lane[start], solve.population.v_lane[start]])
    assert np.unique(lanes).size == 2 * n_new_base_tuples


def test_the_random_starting_selection_of_the_largest_size_uses_every_free_lane():
    """At size 1024, the 192 new base tuples fill the 384 free lanes, when every off-diagonal fine cell of the free
    lanes holds a candidate."""
    # --- arrange ----------------------
    lanes = np.random.default_rng(6).permutation(N_LOWER_FINE_LANES)[:128]
    required_base_tuple_array = np.column_stack([lanes[0::2] + 0.5, lanes[1::2] + 0.5]) / N_FINE_LANES
    solve = _solve(MCTuplesSize.SIZE_1024, required_base_tuple_array, n_population=384 * 384)

    # --- act --------------------------
    start = solve._initial_new_selection()

    # --- assert -----------------------
    new_lanes = np.concatenate([solve.population.u_lane[start], solve.population.v_lane[start]])
    assert np.sort(new_lanes).tolist() == solve.free_lanes.tolist()


def test_the_random_starting_selection_needs_enough_candidates():
    """A population of 2 candidates holds at most 2 new base tuples, too few for the 3 of size 16, and raises an
    error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=2)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="candidates with unused lanes, for 3 new base tuples"):
        solve._initial_new_selection()


# ==================================================================================================
#  Validation
# ==================================================================================================
def test_validation_returns_a_valid_selection_s_new_candidates():
    """A selection of the dummy rotational sibling tuple, the size below's base tuple and 3 candidates in distinct
    lanes meets the constraints of size 16, and its new candidates come back as they are."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)
    new = np.sort(_distinct_lane_selection(solve, 3))

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


def test_validation_refuses_2_new_values_in_1_lane():
    """A size-16 selection of 2 new candidates in distinct lanes and a 3rd that shares a lane with the first raises an
    error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_16, _BASE_4, n_population=8192)
    new = _distinct_lane_selection(solve, 2)
    u_lanes, v_lanes = solve.population.u_lane, solve.population.v_lane
    shares_a_lane = np.flatnonzero((u_lanes == u_lanes[new[0]]) | (v_lanes == u_lanes[new[0]]))
    new = np.sort(np.append(new, shares_a_lane[shares_a_lane != new[0]][0]))

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="a lower fine lane holds 2 or more new values"):
        solve._validated_new_selection(np.concatenate([[0, 1], 2 + new]))
