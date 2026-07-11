import math

import pytest

from sunnbear.errors import DivergedError, FunctionDomainError, MaxFevalsExceeded
from sunnbear.solvers import WrappedFunction


def test_counts_evaluations():
    # --- arrange ----------------------
    wf = WrappedFunction(lambda x: x, a=0.0, b=1.0, max_fevals=10)

    # --- act --------------------------
    for x in (0.1, 0.2, 0.3):
        wf(x)

    # --- assert -----------------------
    assert wf.n_fevals == 3


def test_enforces_max_fevals():
    # --- arrange ----------------------
    wf = WrappedFunction(lambda x: x, a=0.0, b=1.0, max_fevals=2)
    wf(0.1)
    wf(0.2)

    # --- act / assert -----------------
    with pytest.raises(MaxFevalsExceeded):
        wf(0.3)
    assert wf.n_fevals == 2  # the rejected call is not counted


def test_divergence_guard():
    # --- arrange ----------------------
    wf = WrappedFunction(lambda x: x, a=0.0, b=1.0, max_fevals=10)

    # --- act / assert -----------------
    wf(-5.0)  # within guard margin
    with pytest.raises(DivergedError):
        wf(100.0)


def test_domain_guard():
    # --- arrange ----------------------
    wf = WrappedFunction(lambda x: math.nan, a=0.0, b=1.0, max_fevals=10)

    # --- act / assert -----------------
    with pytest.raises(FunctionDomainError):
        wf(0.5)


def test_negation_applies_to_values_and_history():
    # --- arrange ----------------------
    wf = WrappedFunction(lambda x: x + 1.0, a=0.0, b=1.0, max_fevals=10, record_history=True)
    before = wf(0.0)

    # --- act --------------------------
    wf.enable_negation()
    after = wf(1.0)

    # --- assert -----------------------
    assert before == pytest.approx(1.0)
    assert after == pytest.approx(-2.0)
    assert wf.history == [(0.0, -1.0), (1.0, -2.0)]  # earlier entry retroactively flipped


def test_history_disabled_by_default():
    # --- arrange ----------------------
    wf = WrappedFunction(lambda x: x, a=0.0, b=1.0, max_fevals=10)

    # --- act --------------------------
    wf(0.5)

    # --- assert -----------------------
    assert wf.history is None
