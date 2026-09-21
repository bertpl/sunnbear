import math

import pytest
from counted_float import CountedFloat, FlopCountingContext

from sunnbear._core.solvers.core.wrapped_function import WrappedFunction
from sunnbear.exceptions import DivergedError, FunctionDomainError, MaxFevalsExceeded


def _linear(x: float) -> float:
    return 2.0 * x - 1.0


def _wrap(f=_linear, max_fevals: int = 10, record_history: bool = False):
    return WrappedFunction(f, max_fevals=max_fevals, record_history=record_history)


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
def test_far_from_the_origin_is_still_evaluated():
    # --- arrange ----------------------
    wf = _wrap()

    # --- act --------------------------
    wf(1e300)

    # --- assert -----------------------
    assert wf.n_fevals == 1  # No bound on x other than finiteness.


@pytest.mark.parametrize("x", [math.nan, math.inf, -math.inf])
def test_non_finite_x_is_divergence(x):
    # --- arrange ----------------------
    wf = _wrap()

    # --- act / assert -----------------
    with pytest.raises(DivergedError):
        wf(x)
    assert wf.n_fevals == 0  # The call was refused before evaluating.


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_value_is_a_domain_error_and_still_counts(value):
    # --- arrange ----------------------
    wf = _wrap(f=lambda x: value)

    # --- act / assert -----------------
    with pytest.raises(FunctionDomainError) as excinfo:
        wf(0.5)
    assert wf.n_fevals == 1  # The function was evaluated.
    assert excinfo.value.x == 0.5


def test_a_raising_function_is_a_domain_error_and_still_counts():
    # --- arrange ----------------------
    wf = _wrap(f=math.log)

    # --- act / assert -----------------
    with pytest.raises(FunctionDomainError) as excinfo:
        wf(-1.0)
    assert wf.n_fevals == 1  # The function was called.
    assert excinfo.value.x == -1.0
    assert isinstance(excinfo.value.__cause__, ValueError)


# ==================================================================================================
#  History
# ==================================================================================================
def test_history_is_off_by_default():
    # --- arrange ----------------------
    wf = _wrap()

    # --- act --------------------------
    wf(0.5)

    # --- assert -----------------------
    assert wf.history is None


def test_history_records_the_evaluations_as_plain_float_pairs():
    # --- arrange ----------------------
    wf = _wrap(record_history=True)

    # --- act --------------------------
    wf(CountedFloat(0.0))
    wf(1.0)

    # --- assert -----------------------
    assert wf.history == [(0.0, -1.0), (1.0, 1.0)]
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
