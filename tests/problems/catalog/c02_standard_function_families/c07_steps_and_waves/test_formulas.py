"""These tests cover what the formulas of steps and waves (category 2.7) add to the plain functions:

- the jumps of `HeavisideStep`, `FloorFunction` and `PulseWave`, where ``c`` moves them and where the functions take
  no value 0; the check of how a formula applies ``c`` cannot judge these 3, because they are constant between jumps;
- the sign changes of `SawtoothWave` and `PulseWave`;
- the sum of `SquareWaveFourierPartialSum`, and its 1 root at ``d = 0``;
- the forms of `ButterworthFilterGain` and `ChebyshevFilterGain` beyond the cutoff, which never overflow;
- the Bernstein form of `Smoothstep`.
"""

import itertools
import math

import mpmath
import pytest

from sunnbear._core.problems.core import FormulaRegistry

# mpmath computes the reference values with this many decimal digits.
MPMATH_DIGITS = 50


# ==================================================================================================
#  Jumps
# ==================================================================================================
# Each entry holds a formula's number and the position of the jump that ``c`` moves, as a function of the candidate's
# parameter values and ``c``: the step of `HeavisideStep`, the step of `FloorFunction` at which the sign changes, and
# the up-jump of `PulseWave` at 0.
JUMP_POSITIONS = [
    pytest.param((2, 7, 1), lambda param_values, c: c, id="heaviside_step"),
    pytest.param((2, 7, 2), lambda param_values, c: param_values[0] * c, id="floor_function"),
    pytest.param((2, 7, 4), lambda param_values, c: c, id="pulse_wave"),
]


@pytest.mark.parametrize("formula_number, jump_position", JUMP_POSITIONS)
def test_c_moves_the_jump_and_the_function_takes_no_value_0_beside_it(formula_number, jump_position):
    """At several ``c`` within every candidate's c-range, the function jumps from negative to positive at the position
    that ``c`` gives the jump: it is negative at the float below that position and positive at the float above it, and
    not 0 at the position itself."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number(formula_number)

    # --- act / assert -----------------
    for candidate in formula.build_all_candidates():
        param_values = candidate.id.param_values
        # The pulse wave's c-range is about d/2 wide on each side; the others' are wider than 0.3.
        max_abs_c = 0.25 * param_values[1] if formula_number == (2, 7, 4) else 0.3
        for c in (-max_abs_c, 0.0, max_abs_c):
            x_jump = jump_position(param_values, c)
            assert candidate.xc_fun(math.nextafter(x_jump, -math.inf), c) < 0.0, (candidate.id, c)
            assert candidate.xc_fun(math.nextafter(x_jump, math.inf), c) > 0.0, (candidate.id, c)
            assert candidate.xc_fun(x_jump, c) != 0.0, (candidate.id, c)


@pytest.mark.parametrize(
    "formula_number, n_sign_changes", [((2, 7, 3), lambda n: 4 * n + 1), ((2, 7, 4), lambda n: 2 * n + 1)]
)
def test_waves_change_sign_as_often_as_their_docstrings_say(formula_number, n_sign_changes):
    """At ``c = 0``, `SawtoothWave` changes sign ``4*n + 1`` times, at its roots and its jumps, and `PulseWave` changes
    sign ``2*n + 1`` times, at its jumps.

    The x-values lie between each sign change and the next: the sawtooth's at each root plus and minus 1/4, the pulse
    wave's in the middle of each high and low part. The test covers the candidates with ``n`` up to 64.
    """
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number(formula_number)
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[0] <= 64]

    # --- act / assert -----------------
    for candidate in candidates:
        n = int(candidate.id.param_values[0])
        if formula_number == (2, 7, 3):
            x_values = [k + offset for k in range(-n, n + 1) for offset in (-0.25, 0.25)]
        else:
            d = candidate.id.param_values[1]
            x_values = [
                candidate.a,
                *(k + offset for k in range(n) for offset in (0.5 * d, 0.5 * (1.0 + d))),
                candidate.b,
            ]
        signs = [math.copysign(1.0, candidate.xc_fun(x, 0.0)) for x in x_values]
        changes = sum(1 for sign_before, sign_after in itertools.pairwise(signs) if sign_before != sign_after)
        assert changes == n_sign_changes(n), candidate.id


# ==================================================================================================
#  Fourier partial sum of the square wave
# ==================================================================================================
@pytest.mark.parametrize("n", [1, 7, 64, 1024])
def test_fourier_partial_sum_agrees_with_mpmath(n):
    """`SquareWaveFourierPartialSum` agrees with its sum computed by mpmath, to within 1e-13 of the square wave's
    height."""
    # --- arrange ----------------------
    candidate = FormulaRegistry.formula_from_number((2, 7, 5)).build_candidate((float(n), 0.0))

    # --- act / assert -----------------
    with mpmath.workdps(MPMATH_DIGITS):
        for x in (-0.4, -0.01, 1e-6, 0.03, 0.25, 0.5):
            pi_u = mpmath.pi * mpmath.mpf(x)
            expected = float(
                4 / mpmath.pi * mpmath.fsum(mpmath.sin((2 * k + 1) * pi_u) / (2 * k + 1) for k in range(n))
            )
            assert candidate.xc_fun(x, 0.0) == pytest.approx(expected, rel=1e-12, abs=1e-13), x


def test_fourier_partial_sum_at_level_0_has_1_root():
    """At ``d = 0`` and ``c = 0``, every candidate of `SquareWaveFourierPartialSum` is negative on ``[-1/2, 0)`` and
    positive on ``(0, 1/2]``, at x-values 0.005 apart, so its 1 root lies at 0."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number((2, 7, 5))
    candidates = [candidate for candidate in formula.build_all_candidates() if candidate.id.param_values[1] == 0.0]
    x_values = [0.005 * i for i in range(1, 101)]

    # --- act / assert -----------------
    assert len(candidates) == 96
    for candidate in candidates:
        assert all(candidate.xc_fun(x, 0.0) > 0.0 for x in x_values), candidate.id
        assert all(candidate.xc_fun(-x, 0.0) < 0.0 for x in x_values), candidate.id


# ==================================================================================================
#  Filter gains
# ==================================================================================================
# Each entry holds a formula's number and its gain in the plain form, which overflows for a high order beyond 1.
PLAIN_GAINS = [
    pytest.param((2, 7, 6), lambda u, n: 1.0 / math.sqrt(1.0 + u ** (2 * n)), id="butterworth"),
    pytest.param((2, 7, 7), lambda u, n: 1.0 / math.sqrt(1.0 + math.cosh(n * math.acosh(u)) ** 2), id="chebyshev"),
]


@pytest.mark.parametrize("formula_number, plain_gain", PLAIN_GAINS)
@pytest.mark.parametrize("n", [1, 2, 5, 16, 64])
def test_filter_gain_beyond_the_cutoff_agrees_with_its_plain_form(formula_number, plain_gain, n):
    """Beyond the cutoff, where the plain form does not overflow, the filter gain, at the level 0, agrees with it to
    within a relative 1e-12."""
    # --- arrange ----------------------
    gain = FormulaRegistry.formula_from_number(formula_number).bind_xc_fun((float(n), 0.0))

    # --- act / assert -----------------
    for u in (1.0 + 1e-9, 1.001, 1.1, 1.5, 2.0):
        assert gain(u, 0.0) == pytest.approx(plain_gain(u, n), rel=1e-12, abs=0.0), u


@pytest.mark.parametrize("formula_number", [(2, 7, 6), (2, 7, 7)])
def test_filter_gain_is_minus_d_far_beyond_the_cutoff_at_its_highest_order(formula_number):
    """At the highest order of its sweep of the order, the filter gain is exactly ``-d`` at the upper bound, where its
    plain form would overflow."""
    # --- arrange ----------------------
    formula = FormulaRegistry.formula_from_number(formula_number)
    candidate = max(formula.build_all_candidates(), key=lambda candidate: candidate.id.param_values[0])

    # --- act --------------------------
    value = candidate.xc_fun(2.0, 0.0)

    # --- assert -----------------------
    assert value == -candidate.id.param_values[1]


# ==================================================================================================
#  Smoothstep
# ==================================================================================================
# Each entry holds an order and the smoothstep of that order in its usual form.
SMOOTHSTEPS = [
    pytest.param(0, lambda t: t, id="clamped_line"),
    pytest.param(1, lambda t: 3 * t**2 - 2 * t**3, id="smoothstep"),
    pytest.param(2, lambda t: 6 * t**5 - 15 * t**4 + 10 * t**3, id="smootherstep"),
]


@pytest.mark.parametrize("n, smoothstep", SMOOTHSTEPS)
def test_smoothstep_agrees_with_its_usual_form(n, smoothstep):
    """The Bernstein form of `Smoothstep`, at the level 0, agrees with the usual form of orders 0, 1 and 2 to within a
    relative 1e-12."""
    # --- arrange ----------------------
    smoothstep_n = FormulaRegistry.formula_from_number((2, 7, 8)).bind_xc_fun((float(n), 4.0, 0.0))

    # --- act / assert -----------------
    for x in (1e-6 - 0.5, -0.4, -0.25, 0.0, 0.2, 0.499):
        # The formula's argument, as it computes it from x at c = 0.
        t = x + 0.5
        assert smoothstep_n(x, 0.0) == pytest.approx(smoothstep(t), rel=1e-12, abs=0.0), x


@pytest.mark.parametrize("n", [1, 16, 1024])
def test_smoothstep_is_symmetric_about_its_middle(n):
    """``S_n(1 - t) = 1 - S_n(t)`` to within 1e-12 for orders up to 2^10, so the sum of the Bernstein form keeps its
    precision at a high order."""
    # --- arrange ----------------------
    smoothstep_n = FormulaRegistry.formula_from_number((2, 7, 8)).bind_xc_fun((float(n), 4.0, 0.0))

    # --- act / assert -----------------
    for t in (0.01, 0.2, 0.45, 0.49):
        assert smoothstep_n(t - 0.5, 0.0) + smoothstep_n(0.5 - t, 0.0) == pytest.approx(1.0, abs=1e-12), t
