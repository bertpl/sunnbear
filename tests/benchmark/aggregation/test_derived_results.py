"""`add_derived_results` adds the derived columns of a results table."""

import polars as pl
import pytest
from counted_float import FlopType, FlopWeights
from counted_float.config import get_active_flop_weights, set_active_flop_weights

from sunnbear._core.benchmark.aggregation import (
    DERIVED_RESULTS_SCHEMA,
    FEVAL_FLOP_COSTS,
    add_derived_results,
    total_flop_cost_column_name,
)
from sunnbear._core.benchmark.runner import RESULTS_SCHEMA, solver_flop_count_column_name
from sunnbear._core.solvers.core import SolveStatus

from .results_table import results_table

_ADD_COUNT_COLUMN = solver_flop_count_column_name(FlopType.ADD)
_MUL_COUNT_COLUMN = solver_flop_count_column_name(FlopType.MUL)


@pytest.fixture
def unit_weights_with_mul_at_3():
    """Set counted-float's active flop weights to 1 for every flop type but 3 for MUL, and restore them afterwards."""
    original_weights = get_active_flop_weights()
    set_active_flop_weights(FlopWeights(weights=dict.fromkeys(FlopType, 1.0) | {FlopType.MUL: 3.0}))
    yield
    set_active_flop_weights(original_weights)


@pytest.mark.parametrize("is_lazy", [False, True])
def test_the_derived_columns_are_added_to_a_frame_of_the_same_kind(is_lazy):
    """A `DataFrame` gives a `DataFrame` and a `LazyFrame` a `LazyFrame`, with the derived columns added."""
    # --- arrange ----------------------
    frame = results_table([{}])

    # --- act --------------------------
    derived = add_derived_results(frame.lazy() if is_lazy else frame)

    # --- assert -----------------------
    assert isinstance(derived, pl.LazyFrame if is_lazy else pl.DataFrame)
    assert dict(derived.collect_schema()) == RESULTS_SCHEMA | DERIVED_RESULTS_SCHEMA


@pytest.mark.parametrize(
    "status, is_correct, expected_n_fevals_eff",
    [("converged", True, 10)] + [(status.value, False, 160) for status in SolveStatus],
)
def test_only_a_correct_solve_keeps_its_evaluation_count(status, is_correct, expected_n_fevals_eff):
    """`n_fevals_eff` is `n_fevals` for a converged, correct solve, and the row's `max_fevals` for any other."""
    # --- arrange ----------------------
    frame = results_table([{"status": status, "is_correct": is_correct, "n_fevals": 10, "max_fevals": 160}])

    # --- act / assert -----------------
    assert add_derived_results(frame)["n_fevals_eff"].item() == expected_n_fevals_eff


@pytest.mark.usefixtures("unit_weights_with_mul_at_3")
@pytest.mark.parametrize("is_correct", [True, False])
def test_the_flop_costs_weight_the_counts_and_add_the_evaluations(is_correct):
    """`solver_flop_cost` weights each count, also for a failed solve; `total_flop_cost_feval<k>` adds `k` flops per
    evaluation."""
    # --- arrange ----------------------
    frame = results_table([{"is_correct": is_correct, _ADD_COUNT_COLUMN: 5, _MUL_COUNT_COLUMN: 2}])
    n_fevals_eff = 10 if is_correct else 160

    # --- act --------------------------
    derived = add_derived_results(frame)

    # --- assert -----------------------
    assert derived["solver_flop_cost"].item() == 5 * 1.0 + 2 * 3.0
    for feval_flop_cost in FEVAL_FLOP_COSTS:
        assert derived[total_flop_cost_column_name(feval_flop_cost)].item() == 11.0 + feval_flop_cost * n_fevals_eff


@pytest.mark.usefixtures("unit_weights_with_mul_at_3")
def test_the_weights_are_read_when_add_derived_results_is_called():
    """A lazy frame keeps the weights that were active when it was built, whatever is active when it is collected."""
    # --- arrange ----------------------
    derived = add_derived_results(results_table([{_MUL_COUNT_COLUMN: 2}]).lazy())

    # --- act --------------------------
    set_active_flop_weights(FlopWeights(weights=dict.fromkeys(FlopType, 100.0)))

    # --- assert -----------------------
    assert derived.collect()["solver_flop_cost"].item() == 2 * 3.0


@pytest.mark.usefixtures("unit_weights_with_mul_at_3")
def test_unknown_flop_weights_are_refused():
    """An unknown (NaN) active flop weight raises `ValueError`, since every cost would become NaN."""
    # --- arrange ----------------------
    set_active_flop_weights(FlopWeights(weights={FlopType.ADD: 1.0}))

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="unknown"):
        add_derived_results(results_table([{}]))
