"""`calibrate_c_range` finds the widest c-range in which both endpoint values keep their signs and more than 1/10 of
their magnitudes at ``c = 0``, or returns the `RejectionReason` of the step that rejects the candidate."""

import math

import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuples
from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import RejectionReason
from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation import check2_c_range_calibration
from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation.check2_c_range_calibration import (
    MAX_BOUND_REL_GAP,
    calibrate_c_range,
)

# The 2 c-values of this tuple set lie inside every c-range of these tests, except where a test chooses its own.
_MC_TUPLES = MCTuples(u=[0.5, 0.5], v=[0.25, 0.75])

# On [-1, 1], `_step_xc_fun` gives the c-range [-127/128, 127/128] exactly: the doubling first fails at abs(c) = 1, and
# halving [1/2, 1] stops at [127/128, 1], whose ends differ by less than 1%.
_STEP_C_MAX = 127 / 128


def _step_xc_fun(x: float, c: float) -> float:
    """Return ``x`` for ``abs(c) < 1``, and NaN, which fails the condition, elsewhere."""
    if abs(c) < 1.0:
        return x
    else:
        return math.nan


@pytest.mark.parametrize(
    "xc_fun",
    [
        pytest.param(lambda x, c: x - c, id="increasing"),
        pytest.param(lambda x, c: c - x, id="decreasing"),
    ],
)
def test_the_c_range_ends_where_an_endpoint_value_falls_to_1_10_of_its_value_at_0(xc_fun):
    """For ``x - c`` and ``c - x`` on [-1, 1], an endpoint value falls to 1/10 of its value at ``c = 0`` at
    ``abs(c) = 0.9``, so each bound lies below 0.9, within the halving's last gap of 1%."""
    # --- act --------------------------
    c_range = calibrate_c_range(xc_fun, -1.0, 1.0, mc_tuples=_MC_TUPLES)

    # --- assert -----------------------
    assert isinstance(c_range, CRange)
    for bound in (-c_range.c_min, c_range.c_max):
        assert 0.9 / (1 + MAX_BOUND_REL_GAP) < bound < 0.9


@pytest.mark.parametrize(
    "xc_fun, a, b, reason_expected",
    [
        # Step 1: f(a, 0) and f(b, 0) are not both finite and nonzero, with opposite signs.
        pytest.param(
            lambda x, c: x + 2.0, -1.0, 1.0, RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0, id="same_sign"
        ),
        pytest.param(lambda x, c: x, 0.0, 1.0, RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0, id="zero_at_a"),
        pytest.param(
            lambda x, c: x if x > 0.0 else math.nan,
            -1.0,
            1.0,
            RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0,
            id="nan_at_a",
        ),
        pytest.param(
            lambda x, c: math.log(x + 2.0),
            -2.0,
            1.0,
            RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0,
            id="raises_at_a",
        ),
        pytest.param(
            lambda x, c: (x + 0.5) ** 0.5 - 1.0,
            -1.0,
            1.0,
            RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0,
            id="complex_at_a",
        ),
        # Step 2: an endpoint value changes sign at abs(c) = 1e-10, below the first probe.
        pytest.param(
            lambda x, c: x - 1e10 * c,
            -1.0,
            1.0,
            RejectionReason.CALIBRATION_FAILS_AT_FIRST_PROBE,
            id="sign_change_below_the_first_probe",
        ),
        # Step 3: the condition still holds at the last probe on a side of c = 0.
        pytest.param(
            lambda x, c: x, -1.0, 1.0, RejectionReason.CALIBRATION_NO_BOUND_FOUND, id="no_bound_on_both_sides"
        ),
        pytest.param(
            lambda x, c: x - c if c < 0.0 else x,
            -1.0,
            1.0,
            RejectionReason.CALIBRATION_NO_BOUND_FOUND,
            id="no_bound_on_the_positive_side",
        ),
        # Step 6: f(1, c) = 1 - 1e4*c falls to 1/10 of f(1, 0) at c = 9e-5, and f(-1, c) falls to 1/10 of f(-1, 0) at
        # c = -9e-5, so the bounds lie just inside abs(c) = 9e-5 and the c-range is about 1.8e-4 wide.
        pytest.param(
            lambda x, c: x - 1e4 * c,
            -1.0,
            1.0,
            RejectionReason.CALIBRATION_C_RANGE_TOO_NARROW,
            id="c_range_narrower_than_the_minimum",
        ),
    ],
)
def test_calibration_rejects_a_candidate_with_the_reason_of_the_step_that_fails(xc_fun, a, b, reason_expected):
    """Steps 1 to 3 and step 6 each reject a candidate that fails there, with that step's `RejectionReason`."""
    # --- act --------------------------
    result = calibrate_c_range(xc_fun, a, b, mc_tuples=_MC_TUPLES)

    # --- assert -----------------------
    assert result == reason_expected


@pytest.mark.parametrize(
    "max_returns_to_halving, result_expected",
    [
        pytest.param(
            check2_c_range_calibration.MAX_RETURNS_TO_HALVING,
            CRange(c_min=-_STEP_C_MAX, c_max=0.25),
            id="narrows_the_c_range",
        ),
        pytest.param(0, RejectionReason.CALIBRATION_FAILS_AT_BENCHMARK_C_VALUES, id="rejects_after_the_last_return"),
    ],
)
def test_a_benchmark_c_value_that_fails_narrows_the_c_range_or_rejects_the_candidate(
    max_returns_to_halving, result_expected, monkeypatch
):
    """The condition fails within (0.25, 0.5), between 2 probes, so the search misses it; the benchmark c-value of
    about 0.4 fails, and the return to the halving narrows the range on the positive side to 0.25, the probe below it.
    With no return to the halving allowed, that c-value rejects the candidate."""

    # --- arrange ----------------------
    def xc_fun(x: float, c: float) -> float:
        if 0.25 < c < 0.5:
            return math.nan
        else:
            return _step_xc_fun(x, c)

    monkeypatch.setattr(check2_c_range_calibration, "MAX_RETURNS_TO_HALVING", max_returns_to_halving)
    # On [-127/128, 127/128], v = 0.7 maps to c = 0.397, which fails; v = 0.2 maps to c = -0.595, which passes.
    mc_tuples = MCTuples(u=[0.5, 0.5], v=[0.7, 0.2])

    # --- act --------------------------
    result = calibrate_c_range(xc_fun, -1.0, 1.0, mc_tuples=mc_tuples)

    # --- assert -----------------------
    assert result == result_expected


def test_calibration_rejects_a_candidate_when_a_benchmark_c_value_closer_to_0_than_the_first_probe_fails():
    """When a benchmark c-value closer to 0 than the first probe fails, no evaluated c-value between it and 0 meets
    the condition, so no return to the halving can place a bound below it."""

    # --- arrange ----------------------
    def xc_fun(x: float, c: float) -> float:
        if 0.0 < c < 2.0**-33:
            return math.nan
        else:
            return _step_xc_fun(x, c)

    # On [-127/128, 127/128], v = 0.5 + 2^-40 maps to c = 127 * 2^-46, between 0 and 2^-33.
    mc_tuples = MCTuples(u=[0.5, 0.5], v=[0.5 + 2.0**-40, 0.2])

    # --- act --------------------------
    result = calibrate_c_range(xc_fun, -1.0, 1.0, mc_tuples=mc_tuples)

    # --- assert -----------------------
    assert result == RejectionReason.CALIBRATION_FAILS_AT_BENCHMARK_C_VALUES
