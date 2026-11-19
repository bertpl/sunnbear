"""`MCTuplesRefinementSolve` requires 1 new base tuple in each selected new base tuple's LHS cell of the largest size,
starts from those base tuples, and refuses a selection that breaks an LHS cell's constraint."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesConstructionError, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.refinement import MCTuplesRefinementSolve
from sunnbear._core.benchmark.mc_tuples.construction.solve import INCLUSION_CONSTRAINT_WEIGHT, MCTuplesSolveSettings

# The base tuples use 32 lower-half LHS lanes of size 1024, 16 apart: the 4 base tuples of size 16 take the first 8, the
# 12 new base tuples of size 64 the other 24; u lies in the even ones, v in the odd ones.
_LANES = 5 + 16 * np.arange(32)
_BASE_16 = np.column_stack([_LANES[0:8:2] + 0.5, _LANES[1:8:2] + 0.25]) / 1024
_NEW_OF_SIZE_64 = np.column_stack([_LANES[8::2] + 0.5, _LANES[9::2] + 0.25]) / 1024

_N_RANDOM_CANDIDATES_PER_CELL = 8


def _solve() -> MCTuplesRefinementSolve:
    """Return the refinement of size 64 on `_BASE_16`, with `_NEW_OF_SIZE_64` as the selected new base tuples."""
    settings = MCTuplesSolveSettings(n_workers=1, seed=42, rng=np.random.default_rng(5))
    selected_base_tuple_array = np.vstack([_BASE_16, _NEW_OF_SIZE_64])
    return MCTuplesRefinementSolve(
        _N_RANDOM_CANDIDATES_PER_CELL, selected_base_tuple_array, MCTuplesSize.SIZE_64, settings
    )


# ==================================================================================================
#  Constraints and starting selection
# ==================================================================================================
def test_constraints_hold_1_new_base_tuple_per_lhs_cell_and_the_dummy_rotational_sibling_tuple_and_the_size_below():
    """Size 64 gets 1 constraint per LHS cell of its 12 new base tuples, each over that cell's 9 candidates, and the
    weighted constraint that keeps the dummy rotational sibling tuple and the 4 base tuples of the size below."""
    # --- act --------------------------
    constraints = _solve()._constraints()

    # --- assert -----------------------
    assert len(constraints) == 12 + 1
    for cell, constraint in enumerate(constraints[:-1]):
        assert constraint.int_set == set(range(5 + 9 * cell, 5 + 9 * (cell + 1)))
        assert constraint.min_count == constraint.max_count == 1
    inclusion = constraints[-1]
    assert inclusion.int_set == set(range(5))
    assert inclusion.weight == INCLUSION_CONSTRAINT_WEIGHT


def test_the_starting_selection_is_the_selected_new_base_tuples():
    """The starting selection holds the first candidate of each LHS cell, which is the selected new base tuple in that
    cell."""
    # --- arrange ----------------------
    solve = _solve()

    # --- act --------------------------
    start = solve._initial_new_selection()

    # --- assert -----------------------
    assert start.tolist() == (9 * np.arange(12)).tolist()
    assert np.array_equal(solve.population.base_tuple_array[start], _NEW_OF_SIZE_64)


# ==================================================================================================
#  Validation
# ==================================================================================================
def test_validation_returns_a_selection_with_1_new_base_tuple_per_lhs_cell():
    """Validating a selection of the 5 kept candidates and the last candidate of each LHS cell returns those last
    candidates."""
    # --- arrange ----------------------
    new = 9 * np.arange(12) + 8

    # --- act / assert -----------------
    assert _solve()._validated_new_selection(np.concatenate([np.arange(5), 5 + new])).tolist() == new.tolist()


def test_validation_refuses_2_new_base_tuples_in_1_lhs_cell():
    """A selection that takes 2 candidates of the first LHS cell, and none of the second, raises an error."""
    # --- arrange ----------------------
    new = 9 * np.arange(12)
    new[1] = 1

    # --- act / assert -----------------
    with pytest.raises(
        MCTuplesConstructionError, match="2 LHS cells of the largest size do not hold exactly 1 new base tuple"
    ):
        _solve()._validated_new_selection(np.concatenate([np.arange(5), 5 + np.sort(new)]))
