"""`generate_mc_tuples` builds a nested, bin-balanced tuple set, and refuses a selection breaking its constraints."""

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesConstructionError, MCTuplesSize, generate_mc_tuples
from sunnbear._core.benchmark.mc_tuples.construction import _draw_population
from sunnbear._core.benchmark.mc_tuples.max_div_selection import _check_selection


@pytest.mark.only_with_numba_jit
def test_generate_mc_tuples_builds_a_set_whose_every_size_meets_its_bin_constraints():
    """A 1 s construction gives distinct tuples of the largest size, and every prefix size keeps each bin within 1.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- act --------------------------
    tuples = generate_mc_tuples(t_total_sec=1.0)

    # --- assert -----------------------
    assert tuples.size == max(MCTuplesSize)
    assert np.unique(np.column_stack([tuples.u, tuples.v]), axis=0).shape[0] == tuples.size
    for size in MCTuplesSize:
        assert tuples.first(size).stats().max_bin_count_deviation <= 1


def test_a_smaller_population_is_a_prefix_of_the_full_one():
    """The population for a short run is the start of the full population, all inside the open unit square."""
    # --- act --------------------------
    small = _draw_population(2048, seed=42)
    full = _draw_population(65_536, seed=42)

    # --- assert -----------------------
    assert small.shape == (2048, 2)
    assert (small == full[:2048]).all()
    assert ((full > 0) & (full < 1)).all()


# ==================================================================================================
#  Checks on a selection
# ==================================================================================================
# The population has 24 tuples, 3 per bin on each axis: selecting every third tuple puts 1 in each bin,
# and selecting the first 8 puts 3 in each of 2 bins.
_POPULATION = np.column_stack([(np.arange(24) + 0.5) / 24, (np.arange(24)[::-1] + 0.5) / 24])
_ONE_PER_BIN = np.arange(0, 24, 3)


@pytest.mark.parametrize(
    "required_indices, selection, message",
    [
        (np.array([], dtype=np.int64), np.array([0, 0, 3, 6, 9, 12, 15, 18]), "7 distinct tuples"),
        (np.array([1]), _ONE_PER_BIN, "1 tuples of the size below it are not selected"),
        (np.array([], dtype=np.int64), np.arange(8), "bin counts"),
    ],
)
def test_check_selection_refuses_duplicates_a_missing_tuple_or_unbalanced_bins(required_indices, selection, message):
    """A repeated tuple, a missing tuple of the size below, or a bin off by more than 1 raises an error."""
    with pytest.raises(MCTuplesConstructionError, match=message):
        _check_selection(_POPULATION, 8, required_indices, selection)


def test_check_selection_accepts_a_selection_that_meets_every_constraint():
    """A selection of 8 tuples, 1 per bin on each axis, that includes the required tuple passes the checks."""
    _check_selection(_POPULATION, 8, np.array([3]), _ONE_PER_BIN)
