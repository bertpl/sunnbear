import math

import pytest
from counted_float import CountedFloat, FlopCountingContext

from sunnbear.errors import DivergedError, FunctionDomainError, MaxFevalsExceeded
from sunnbear.solvers._wrapped_function import DIVERGENCE_GUARD_MARGIN, WrappedFunction


def _linear(x: float) -> float:
    return 2.0 * x - 1.0


def _wrap(f=_linear, a: float = 0.0, b: float = 1.0, max_fevals: int = 10, record_history: bool = False):
    return WrappedFunction(f, a, b, max_fevals=max_fevals, record_history=record_history)


# ==================================================================================================
#  Counting and the budget
# ==================================================================================================
def test_counts_evaluations_and_returns_counted_values():
    # --- arrange ----------------------
    wf = _wrap()

    # --- act --------------------------
    values = [wf(0.0), wf(0.5), wf(1.0)]

    # --- assert -----------------------
    assert wf.n_fevals == 3
    assert values == [-1.0, 0.0, 1.0]
    assert all(isinstance(v, CountedFloat) for v in values)


def test_budget_refuses_the_call_that_would_exceed_it():
    # --- arrange ----------------------
    wf = _wrap(max_fevals=2)
    wf(0.0)
    wf(1.0)

    # --- act / assert -----------------
    with pytest.raises(MaxFevalsExceeded):
        wf(0.5)
    assert wf.n_fevals == 2  # The refused call is not an evaluation.


# ==================================================================================================
#  Guards
# ==================================================================================================
@pytest.mark.parametrize("x", [-DIVERGENCE_GUARD_MARGIN, 1.0 + DIVERGENCE_GUARD_MARGIN, 0.5])  # guard edges and inside
def test_guard_interval_edges_are_inside(x):
    # --- arrange ----------------------
    wf = _wrap(a=0.0, b=1.0)

    # --- act --------------------------
    wf(x)

    # --- assert -----------------------
    assert wf.n_fevals == 1


@pytest.mark.parametrize("x", [-DIVERGENCE_GUARD_MARGIN - 1e-9, 1.0 + DIVERGENCE_GUARD_MARGIN + 1e-9])
def test_outside_the_guard_interval_is_divergence(x):
    # --- arrange ----------------------
    wf = _wrap(a=0.0, b=1.0)

    # --- act / assert -----------------
    with pytest.raises(DivergedError):
        wf(x)
    assert wf.n_fevals == 0  # The call was refused before evaluating.


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_value_is_a_domain_error_and_still_counts(value):
    # --- arrange ----------------------
    wf = _wrap(f=lambda x: value)

    # --- act / assert -----------------
    with pytest.raises(FunctionDomainError):
        wf(0.5)
    assert wf.n_fevals == 1  # The function was evaluated.


# ==================================================================================================
#  Sign normalization and history
# ==================================================================================================
def test_sign_normalization_negates_values_from_then_on():
    # --- arrange ----------------------
    wf = _wrap()
    before = wf(1.0)

    # --- act --------------------------
    wf.enable_sign_normalization()
    after = wf(1.0)

    # --- assert -----------------------
    assert (before, after) == (1.0, -1.0)


def test_history_is_off_by_default():
    # --- arrange ----------------------
    wf = _wrap()

    # --- act --------------------------
    wf(0.5)

    # --- assert -----------------------
    assert wf.history is None


def test_history_records_normalized_plain_float_pairs():
    # --- arrange ----------------------
    wf = _wrap(record_history=True)
    wf.enable_sign_normalization()

    # --- act --------------------------
    wf(CountedFloat(0.0))
    wf(1.0)

    # --- assert -----------------------
    assert wf.history == [(0.0, 1.0), (1.0, -1.0)]
    assert all(type(v) is float for pair in wf.history for v in pair)


# ==================================================================================================
#  Flop accounting
# ==================================================================================================
def test_function_body_flops_are_not_counted():
    """Arithmetic inside f — even on CountedFloat values — must not land in the solver's counts."""
    # --- arrange ----------------------
    wf = _wrap(f=lambda x: CountedFloat(x) * CountedFloat(3.0) + CountedFloat(1.0))

    # --- act --------------------------
    with FlopCountingContext() as ctx:
        wf(CountedFloat(0.5))

    # --- assert -----------------------
    assert ctx.flop_counts().total_count() == 0
