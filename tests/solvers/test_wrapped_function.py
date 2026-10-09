"""These tests assert that `WrappedFunction`:

- counts evaluations against a budget;
- refuses non-finite x-values;
- turns a failing function into `FunctionDomainError`;
- records an optional history;
- leaves the arithmetic of the function uncounted.
"""

import math

import pytest
from counted_float import CountedFloat, FlopCountingContext

from sunnbear._core.solvers.core.wrapped_function import WrappedFunction
from sunnbear.exceptions import DivergedError, FunctionDomainError, MaxFevalsExceeded


def _linear(x: float) -> float:
    """Return the value of a linear function with its root at 0.5."""
    return 2.0 * x - 1.0


def _wrap(f=_linear, max_fevals: int = 10, history_enabled: bool = False):
    """Return a `WrappedFunction` around ``f`` with the given budget and history setting."""
    return WrappedFunction(f, max_fevals=max_fevals, history_enabled=history_enabled)


# ==================================================================================================
#  Counting and the budget
# ==================================================================================================
def test_counts_evaluations_and_returns_counted_values():
    """Each call counts 1 evaluation and returns the function value as a `CountedFloat`."""
    # --- arrange ----------------------
    wf = _wrap()

    # --- act --------------------------
    values = [wf(0.0), wf(0.5), wf(1.0)]

    # --- assert -----------------------
    assert wf.n_fevals == 3
    assert values == [-1.0, 0.0, 1.0]
    assert all(isinstance(v, CountedFloat) for v in values)


def test_budget_refuses_the_call_that_would_exceed_it():
    """With a budget of 2 evaluations, the 3rd call raises `MaxFevalsExceeded` and is not counted."""
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
    """A finite x-value as far from the origin as 1e300 is evaluated and counted."""
    # --- arrange ----------------------
    wf = _wrap()

    # --- act --------------------------
    wf(1e300)

    # --- assert -----------------------
    assert wf.n_fevals == 1  # No bound on x other than finiteness.


@pytest.mark.parametrize("x", [math.nan, math.inf, -math.inf])
def test_non_finite_x_is_divergence(x):
    """A NaN or infinite x-value raises `DivergedError` before the function is evaluated, so nothing is counted."""
    # --- arrange ----------------------
    wf = _wrap()

    # --- act / assert -----------------
    with pytest.raises(DivergedError):
        wf(x)
    assert wf.n_fevals == 0  # The call was refused before evaluating.


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_value_is_a_domain_error_and_still_counts(value):
    """A NaN or infinite function value raises `FunctionDomainError` carrying the x-value, and the evaluation counts."""
    # --- arrange ----------------------
    wf = _wrap(f=lambda x: value)

    # --- act / assert -----------------
    with pytest.raises(FunctionDomainError) as excinfo:
        wf(0.5)
    assert wf.n_fevals == 1  # The function was evaluated.
    assert excinfo.value.x == 0.5


def test_a_raising_function_is_a_domain_error_and_still_counts():
    """An exception raised by the function becomes a `FunctionDomainError` that carries the x-value and is chained to
    the original exception, and the evaluation counts."""
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
    """`WrappedFunction.history` is None when history is not enabled."""
    # --- arrange ----------------------
    wf = _wrap()

    # --- act --------------------------
    wf(0.5)

    # --- assert -----------------------
    assert wf.history is None


def test_history_records_the_evaluations_as_plain_float_pairs():
    """With history enabled, each evaluation is recorded as an ``(x, f(x))`` pair of plain floats, also for a
    `CountedFloat` x-value."""
    # --- arrange ----------------------
    wf = _wrap(history_enabled=True)

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
