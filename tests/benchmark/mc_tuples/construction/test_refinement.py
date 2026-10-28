"""`MCTuplesRefinementSolve` requires 1 new base tuple per fine cell of the selected new base tuples, starts from those
base tuples, and refuses a selection that breaks a fine cell's constraint."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, MCTuplesConstructionError, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.refinement import MCTuplesRefinementSolve
from sunnbear._core.benchmark.mc_tuples.construction.solve import INCLUSION_CONSTRAINT_WEIGHT, MCTuplesSolveSettings

# The base tuples use 32 lower fine lanes, 16 apart: the 8 base tuples of size 32 take the first 16, the 8 new base
# tuples of size 64 the other 16; u lies in the even ones, v in the odd ones.
_LANES = 5 + 16 * np.arange(32)
_BASE_32 = np.column_stack([_LANES[0:16:2] + 0.5, _LANES[1:16:2] + 0.25]) / N_FINE_LANES
_NEW_OF_SIZE_64 = np.column_stack([_LANES[16::2] + 0.5, _LANES[17::2] + 0.25]) / N_FINE_LANES

_N_RANDOM_CANDIDATES_PER_CELL = 8


def _solve() -> MCTuplesRefinementSolve:
    """Return the refinement of size 64 on `_BASE_32`, with `_NEW_OF_SIZE_64` as the selected new base tuples."""
    settings = MCTuplesSolveSettings(n_workers=1, seed=42, rng=np.random.default_rng(5))
    selected_base_tuple_array = np.vstack([_BASE_32, _NEW_OF_SIZE_64])
    return MCTuplesRefinementSolve(
        _N_RANDOM_CANDIDATES_PER_CELL, selected_base_tuple_array, MCTuplesSize.SIZE_64, settings
    )


# ==================================================================================================
#  Constraints and starting selection
# ==================================================================================================
def test_constraints_hold_exactly_1_new_base_tuple_per_fine_cell_and_the_placeholder_and_the_size_below():
    """Size 64 gets 1 constraint per fine cell of its 8 new base tuples, each over that cell's 9 candidates, and the
    weighted constraint that keeps the placeholder and the 8 base tuples of the size below."""
    # --- act --------------------------
    constraints = _solve()._constraints()

    # --- assert -----------------------
    assert len(constraints) == 8 + 1
    for cell, constraint in enumerate(constraints[:-1]):
        assert constraint.int_set == set(range(9 + 9 * cell, 9 + 9 * (cell + 1)))
        assert constraint.min_count == constraint.max_count == 1
    inclusion = constraints[-1]
    assert inclusion.int_set == set(range(9))
    assert inclusion.weight == INCLUSION_CONSTRAINT_WEIGHT


def test_the_starting_selection_is_the_selected_new_base_tuples():
    """The starting selection holds the first candidate of each fine cell, which is the selected new base tuple in that
    cell."""
    # --- arrange ----------------------
    solve = _solve()

    # --- act --------------------------
    start = solve._initial_new_selection()

    # --- assert -----------------------
    assert start.tolist() == (9 * np.arange(8)).tolist()
    assert np.array_equal(solve.population.tuple_array[start], _NEW_OF_SIZE_64)


# ==================================================================================================
#  Validation
# ==================================================================================================
def test_validation_returns_a_selection_with_1_new_base_tuple_per_fine_cell():
    """Validating a selection of the 9 kept candidates and the last candidate of each fine cell returns those last
    candidates."""
    # --- arrange ----------------------
    new = 9 * np.arange(8) + 8

    # --- act / assert -----------------
    assert _solve()._validated_new_selection(np.concatenate([np.arange(9), 9 + new])).tolist() == new.tolist()


def test_validation_refuses_2_new_base_tuples_in_1_fine_cell():
    """A selection that takes 2 candidates of the first fine cell, and none of the second, raises an error."""
    # --- arrange ----------------------
    new = 9 * np.arange(8)
    new[1] = 1

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="2 fine cells do not hold exactly 1 new base tuple"):
        _solve()._validated_new_selection(np.concatenate([np.arange(9), 9 + np.sort(new)]))
