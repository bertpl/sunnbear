"""`MCTuplesRefinementSolve` holds 1 new tuple per fine cell of the selection, starts from the selection's tuples, and
refuses a selection that breaks a fine cell's constraint."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import N_FINE_LANES, MCTuplesConstructionError, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction.refinement import MCTuplesRefinementSolve
from sunnbear._core.benchmark.mc_tuples.construction.solve import INCLUSION_CONSTRAINT_WEIGHT, MCTuplesSolveSettings

# The 32 tuples of the smallest size spread from the first fine lane to the last, with u rising and v falling; the
# 32 new tuples of size 64 lie 1 fine lane above each of them on both axes.
_LANES_32 = np.round(np.linspace(0, N_FINE_LANES - 2, 32)).astype(np.int64)
_SIZE_32 = np.column_stack([_LANES_32 + 0.5, _LANES_32[::-1] + 0.25]) / N_FINE_LANES
_NEW_OF_SIZE_64 = _SIZE_32 + 1 / N_FINE_LANES

_N_CANDIDATES_PER_CELL = 8


def _refinement() -> MCTuplesRefinementSolve:
    """Return the refinement of size 64 on `_SIZE_32`, with `_NEW_OF_SIZE_64` as the selection's new tuples."""
    settings = MCTuplesSolveSettings(n_workers=1, seed=42, rng=np.random.default_rng(5))
    return MCTuplesRefinementSolve(_N_CANDIDATES_PER_CELL, _SIZE_32, _NEW_OF_SIZE_64, MCTuplesSize.SIZE_64, settings)


# ==================================================================================================
#  Constraints and starting selection
# ==================================================================================================
def test_constraints_hold_exactly_1_new_tuple_per_fine_cell_and_the_size_below():
    """Size 64 gets 1 constraint per fine cell of its 32 new tuples, each over that cell's 9 candidates, and the
    weighted inclusion of the 32 tuples of the size below."""
    # --- act --------------------------
    constraints = _refinement()._constraints()

    # --- assert -----------------------
    assert len(constraints) == 32 + 1
    for cell, constraint in enumerate(constraints[:-1]):
        assert constraint.int_set == set(range(32 + 9 * cell, 32 + 9 * (cell + 1)))
        assert constraint.min_count == constraint.max_count == 1
    inclusion = constraints[-1]
    assert inclusion.int_set == set(range(32))
    assert inclusion.weight == INCLUSION_CONSTRAINT_WEIGHT


def test_the_starting_selection_is_the_selection_s_new_tuples():
    """The starting selection holds the first candidate of each fine cell, which is the selection's tuple there."""
    # --- arrange ----------------------
    refinement = _refinement()

    # --- act --------------------------
    start = refinement._initial_new_selection()

    # --- assert -----------------------
    assert start.tolist() == (9 * np.arange(32)).tolist()
    assert np.array_equal(refinement.population.tuple_array[start], _NEW_OF_SIZE_64)


# ==================================================================================================
#  Validation
# ==================================================================================================
def test_validation_returns_a_selection_with_1_new_tuple_per_fine_cell():
    """A selection of the last candidate of each fine cell, with the 32 tuples of the size below, comes back as its
    new candidates."""
    # --- arrange ----------------------
    new = 9 * np.arange(32) + 8

    # --- act / assert -----------------
    assert _refinement()._validated_new_selection(np.concatenate([np.arange(32), 32 + new])).tolist() == new.tolist()


def test_validation_refuses_2_new_tuples_in_1_fine_cell():
    """A selection that takes 2 candidates of the first fine cell, and none of the second, raises an error."""
    # --- arrange ----------------------
    new = 9 * np.arange(32)
    new[1] = 1

    # --- act / assert -----------------
    with pytest.raises(MCTuplesConstructionError, match="2 fine cells do not hold exactly 1 new tuple"):
        _refinement()._validated_new_selection(np.concatenate([np.arange(32), 32 + np.sort(new)]))
