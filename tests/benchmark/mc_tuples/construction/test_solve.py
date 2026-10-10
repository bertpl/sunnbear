"""`MCTuplesSizeSolve` builds its constraints and a valid random start, and refuses a selection that breaks them."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, MCTuplesConstructionError, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.allocation import MCTuplesGapAllocation
from sunnbear._core.benchmark.mc_tuples.construction.population import MCTuplesPopulation
from sunnbear._core.benchmark.mc_tuples.construction.solve import (
    INCLUSION_CONSTRAINT_WEIGHT,
    MCTuplesSizeSolve,
    MCTuplesSolveSettings,
)

# The 32 tuples of the smallest size spread from the first fine lane to the last, with u rising and v falling.
_LANES_32 = np.round(np.linspace(0, N_FINE_LANES - 1, 32)).astype(np.int64)
_SIZE_32 = np.column_stack([_LANES_32 + 0.5, _LANES_32[::-1] + 0.25]) / N_FINE_LANES


def _solve(size: MCTuplesSize, required_tuple_array: np.ndarray, n_population: int) -> MCTuplesSizeSolve:
    """Return the solve of `size` on `required_tuple_array`, with a population of `n_population` over its free lanes."""
    rng = np.random.default_rng(5)
    population = MCTuplesPopulation.draw_in_free_lanes(n_population, required_tuple_array, rng)
    return MCTuplesSizeSolve(
        population,
        required_tuple_array,
        size,
        MCTuplesGapAllocation.of(required_tuple_array, size.n_new),
        MCTuplesSolveSettings(n_workers=1, seed=42, rng=rng),
    )


def _distinct_lane_selection(solve: MCTuplesSizeSolve, n: int) -> np.ndarray:
    """Return `n` candidates, as indices into `candidate_indices`, that share no fine lane on either axis."""
    picked, used_u, used_v = [], set(), set()
    for i, candidate in enumerate(solve.candidate_indices):
        u_lane, v_lane = solve.population.u_lane[candidate], solve.population.v_lane[candidate]
        if u_lane not in used_u and v_lane not in used_v:
            picked.append(i)
            used_u.add(u_lane)
            used_v.add(v_lane)
        if len(picked) == n:
            break
    return np.array(picked)


# ==================================================================================================
#  Constraints
# ==================================================================================================
def test_constraints_hold_each_gap_s_count_1_per_fine_lane_in_a_gap_of_several_and_the_size_below():
    """Size 64 gets 1 constraint per gap with new tuples on each axis, 1 per fine lane of each gap that takes 2, and
    the weighted inclusion of the 32 tuples of the size below."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_64, _SIZE_32, n_population=8192)

    # --- act --------------------------
    constraints = solve._constraints()

    # --- assert -----------------------
    n_gaps = solve.gap_allocation.u.counts.size + solve.gap_allocation.v.counts.size
    gap_constraints = constraints[: solve.gap_allocation.u.counts.size]
    assert sorted(c.min_count for c in gap_constraints) == sorted(solve.gap_allocation.u.counts.tolist())
    assert all(c.min_count == c.max_count for c in gap_constraints)
    fine_lane_constraints = [c for c in constraints[:-1] if c.min_count == 0]
    assert len(fine_lane_constraints) == len(constraints) - 1 - n_gaps
    assert all(c.max_count == 1 for c in fine_lane_constraints)
    inclusion = constraints[-1]
    assert inclusion.int_set == set(range(32))
    assert inclusion.min_count == inclusion.max_count == 32
    assert inclusion.weight == INCLUSION_CONSTRAINT_WEIGHT


def test_constraints_leave_out_the_fine_lanes_when_every_gap_takes_at_most_1():
    """Tuples of the size below every 32 fine lanes from lane 16 leave 33 gaps for 32 new tuples, so no gap takes 2
    and no fine lane needs a constraint of its own."""
    # --- arrange ----------------------
    lanes = 16 + 32 * np.arange(32)
    solve = _solve(MCTuplesSize.SIZE_64, np.column_stack([lanes + 0.5, lanes + 0.5]) / N_FINE_LANES, n_population=8192)

    # --- act --------------------------
    constraints = solve._constraints()

    # --- assert -----------------------
    assert solve.gap_allocation.u.counts.max() == solve.gap_allocation.v.counts.max() == 1
    assert len(constraints) == solve.gap_allocation.u.counts.size + solve.gap_allocation.v.counts.size + 1


def test_constraints_of_the_smallest_size_hold_its_1_gap_s_count_and_1_tuple_per_fine_lane():
    """Size 32 is 1 gap of 32 new tuples per axis, so every fine lane gets an at-most-1 constraint; with no size
    below, there is no inclusion constraint."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_32, np.zeros((0, 2)), n_population=4096)

    # --- act --------------------------
    constraints = solve._constraints()

    # --- assert -----------------------
    assert len(constraints) == 2 * (1 + N_FINE_LANES)
    assert [c.min_count for c in constraints if c.min_count > 0] == [32, 32]


# ==================================================================================================
#  Random starting selection
# ==================================================================================================
def test_the_random_starting_selection_holds_the_new_tuples_in_distinct_fine_lanes():
    """The starting selection holds as many candidates as the size has new tuples, ascending, each in its own fine
    lane on each axis."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_64, _SIZE_32, n_population=8192)

    # --- act --------------------------
    start = solve._initial_new_selection()

    # --- assert -----------------------
    assert start.size == 32
    assert np.array_equal(start, np.sort(start))
    for lanes in (solve.population.u_lane, solve.population.v_lane):
        assert np.unique(lanes[solve.candidate_indices[start]]).size == 32


def test_the_random_starting_selection_needs_as_many_pairable_fine_lanes_as_new_tuples():
    """A population of 10 candidates cannot place 32 new tuples in distinct fine lanes, which raises an error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_32, np.zeros((0, 2)), n_population=10)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="only 10 fine lanes can be paired"):
        solve._initial_new_selection()


# ==================================================================================================
#  Validation
# ==================================================================================================
def test_validation_returns_a_valid_selection_s_new_candidates():
    """A selection of 32 candidates in distinct fine lanes meets the smallest size's constraints, and comes back as
    it is."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_32, np.zeros((0, 2)), n_population=4096)
    selection = _distinct_lane_selection(solve, 32)

    # --- act / assert -----------------
    assert solve._validated_new_selection(selection).tolist() == selection.tolist()


@pytest.mark.parametrize(
    "selection, message",
    [
        (np.arange(1, 65), "1 tuples of the size below it are not selected"),
        (np.arange(64), "gaps along u do not hold their allocated number"),
    ],
)
def test_validation_refuses_a_size_64_selection_that_breaks_a_constraint(selection, message):
    """A selection that leaves out 1 of the 32 tuples of the size below, or whose first 32 candidates all lie in the
    lowest gaps along u, raises an error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_64, _SIZE_32, n_population=8192)

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match=message):
        solve._validated_new_selection(selection)


def test_validation_refuses_2_new_tuples_in_1_fine_lane():
    """At the smallest size any 32 candidates meet the count of its 1 gap, but 2 in 1 fine lane raise an error."""
    # --- arrange ----------------------
    solve = _solve(MCTuplesSize.SIZE_32, np.zeros((0, 2)), n_population=4096)
    selection = _distinct_lane_selection(solve, 31)
    u_lanes = solve.population.u_lane[solve.candidate_indices]
    shares_u_lane = np.flatnonzero(u_lanes == u_lanes[selection[0]])
    selection = np.sort(np.append(selection, shares_u_lane[shares_u_lane != selection[0]][0]))

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="a fine u-lane holds 2 or more new tuples"):
        solve._validated_new_selection(selection)
