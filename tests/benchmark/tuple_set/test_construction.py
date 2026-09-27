"""`generate_uv_tuples` builds a nested, span-balanced tuple set, and refuses a selection breaking its constraints."""

import numpy as np
import pytest

from sunnbear._core.benchmark.tuple_set import UV_TUPLES_SIZES, UvTuplesConstructionError, generate_uv_tuples
from sunnbear._core.benchmark.tuple_set.construction import _check_selection, _draw_population


def test_generate_uv_tuples_builds_a_set_whose_every_size_meets_its_span_constraints():
    """A 1 s construction gives 1024 distinct tuples whose every prefix size keeps each span within 1.

    Only the structure is asserted: max-div's spread depends on the wall-clock time.
    """
    # --- act --------------------------
    tuples = generate_uv_tuples(t_total_sec=1.0)

    # --- assert -----------------------
    assert tuples.size == max(UV_TUPLES_SIZES)
    assert np.unique(np.column_stack([tuples.u, tuples.v]), axis=0).shape[0] == tuples.size
    for size in UV_TUPLES_SIZES:
        assert tuples.first(size).stats().max_span_count_deviation <= 1


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
# The population has 24 tuples, 3 per span on each axis: every third one gives 1 per span, and the first 8
# overfill 2 spans.
_POPULATION = np.column_stack([(np.arange(24) + 0.5) / 24, (np.arange(24)[::-1] + 0.5) / 24])
_ONE_PER_SPAN = np.arange(0, 24, 3)


@pytest.mark.parametrize(
    "required_indices, selection, message",
    [
        (np.array([], dtype=np.int64), np.array([0, 0, 3, 6, 9, 12, 15, 18]), "7 distinct tuples"),
        (np.array([1]), _ONE_PER_SPAN, "1 tuples of the size below it are not selected"),
        (np.array([], dtype=np.int64), np.arange(8), "span counts"),
    ],
)
def test_check_selection_refuses_duplicates_a_missing_tuple_or_unbalanced_spans(required_indices, selection, message):
    """A repeated tuple, a missing tuple of the size below, or a span off by more than 1 raises an error."""
    with pytest.raises(UvTuplesConstructionError, match=message):
        _check_selection(_POPULATION, 8, required_indices, selection)


def test_check_selection_accepts_a_selection_that_meets_every_constraint():
    """A selection of 8 tuples, 1 per span on each axis, that includes the required tuple passes the checks."""
    _check_selection(_POPULATION, 8, np.array([3]), _ONE_PER_SPAN)
