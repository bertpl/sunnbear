import math
import statistics
import struct

import mpmath
import pytest

from sunnbear._core.utils.math_functions import (
    bessel_j0,
    bessel_j1,
    bessel_y0,
    bessel_y1,
    noise,
    normal_noise,
    real_root,
    sign,
    uniform_noise,
)

# _BESSEL_X_VALUES reach each range of the Bessel functions: tiny, up to 5, from 5 to 10, and above 10;
# 2.4048255576957727 is the first zero of J0.
_BESSEL_X_VALUES = [1e-9, 2e-6, 0.5, 2.4048255576957727, 4.99, 5.5, 9.99, 10.5, 31.4, 60.0]


@pytest.mark.parametrize(
    "value, expected",
    [(-2.5, -1.0), (0.0, 0.0), (-0.0, 0.0), (3.0, 1.0)],
)
def test_sign(value, expected):
    """`sign` returns -1, 0 or 1 for a negative, zero or positive value."""
    assert sign(value) == expected


def test_sign_of_nan_is_nan():
    """`sign` returns NaN for NaN."""
    assert math.isnan(sign(math.nan))


@pytest.mark.parametrize(
    "value, n, expected",
    [(-8.0, 3, -2.0), (27.0, 3, 27.0 ** (1 / 3)), (0.0, 5, 0.0), (-32.0, 5, -2.0)],
)
def test_real_root(value, n, expected):
    """`real_root` is negative for a negative value, and the power `value**(1/n)` exactly for the others."""
    assert real_root(value, n) == expected


@pytest.mark.parametrize(
    "bessel_function, order, kind",
    [(bessel_j0, 0, "j"), (bessel_j1, 1, "j"), (bessel_y0, 0, "y"), (bessel_y1, 1, "y")],
)
@pytest.mark.parametrize("x", _BESSEL_X_VALUES)
def test_bessel_function_agrees_with_mpmath(bessel_function, order, kind, x):
    """Each Bessel function is within 2E-15 of mpmath's value in each of its ranges.

    The bound is relative where that value exceeds 1 in magnitude, and absolute elsewhere.
    """
    # --- arrange ----------------------
    with mpmath.workdps(40):
        if kind == "j":
            expected = float(mpmath.besselj(order, x))
        else:
            expected = float(mpmath.bessely(order, x))

    # --- act --------------------------
    value = bessel_function(x)

    # --- assert -----------------------
    assert abs(value - expected) <= 2e-15 * max(1.0, abs(expected))


@pytest.mark.parametrize("x", [-0.5, -7.0, -12.0])
def test_bessel_functions_of_the_first_kind_have_their_parity(x):
    """`bessel_j0` and `bessel_j1` accept a negative argument: J0 is even and J1 is odd."""
    assert bessel_j0(x) == bessel_j0(-x)
    assert bessel_j1(x) == -bessel_j1(-x)


@pytest.mark.parametrize("bessel_function", [bessel_y0, bessel_y1])
def test_bessel_functions_of_the_second_kind_at_0_and_below(bessel_function):
    """Y0 and Y1 are minus infinity at 0 and NaN for a negative x."""
    assert bessel_function(0.0) == -math.inf
    assert math.isnan(bessel_function(-1.0))


# _NOISE_X_VALUES are 10^4 evenly spaced x-values, over which the noise must look like independent random draws; the
# standard error of a mean of 10^4 draws is 1% of their standard deviation.
_NOISE_X_VALUES = [i * 1e-3 - 5.0 for i in range(10_000)]


@pytest.mark.parametrize("noise_function", [uniform_noise, normal_noise])
def test_noise_depends_only_on_x(noise_function):
    """A noise function returns the same value for the same x, and different values for neighboring x-values."""
    # --- arrange ----------------------
    x = 0.37

    # --- act --------------------------
    values = [noise_function(x), noise_function(x), noise_function(math.nextafter(x, 1.0))]

    # --- assert -----------------------
    assert values[0] == values[1]
    assert values[0] != values[2]


def test_uniform_noise_is_spread_as_uniform_draws():
    """`uniform_noise` lies in [0, 1), with a uniform draw's mean 1/2 and variance 1/12, within 4 standard errors."""
    # --- act --------------------------
    values = [uniform_noise(x) for x in _NOISE_X_VALUES]

    # --- assert -----------------------
    assert all(0.0 <= value < 1.0 for value in values)
    assert statistics.mean(values) == pytest.approx(0.5, abs=0.012)
    assert statistics.pvariance(values) == pytest.approx(1 / 12, rel=0.036)


def test_normal_noise_is_spread_as_standard_normal_draws():
    """`normal_noise` has a standard normal draw's mean 0 and standard deviation 1, within 4 standard errors."""
    # --- act --------------------------
    values = [normal_noise(x) for x in _NOISE_X_VALUES]

    # --- assert -----------------------
    assert statistics.mean(values) == pytest.approx(0.0, abs=0.04)
    assert statistics.pstdev(values) == pytest.approx(1.0, rel=0.03)


@pytest.mark.parametrize("noise_function", [uniform_noise, normal_noise])
@pytest.mark.parametrize("x", [math.inf, -math.inf, math.nan])
def test_noise_of_a_non_finite_x_is_nan(noise_function, x):
    """A noise function returns NaN for an infinite or NaN x."""
    assert math.isnan(noise_function(x))


@pytest.mark.parametrize("x", [0.0, -0.0, 1.5, -3.3e-200, 1.5 * 2.0**512, 1.7976931348623157e308, 5e-324, -2.2e-308])
def test_float_bits_are_the_ieee_754_bits(x):
    """`_float_bits` gives the IEEE 754 bits of x, for zeros, normal and subnormal values of either sign."""
    assert int(noise._float_bits(x)) == struct.unpack("<Q", struct.pack("<d", x))[0]
