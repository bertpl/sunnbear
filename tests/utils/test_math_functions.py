import math

import mpmath
import pytest

from sunnbear._core.utils.math_functions import bessel_j0, bessel_j1, bessel_y0, bessel_y1, real_root, sign

# _BESSEL_X_VALUES reach each range of the Bessel functions: tiny, up to 5, from 5 to 10, and above 10.
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
    """Each Bessel function is within 2E-15 of mpmath's, relative above 1 and absolute below, in each of its ranges."""
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
    """J0 is even and J1 is odd, so both take negative arguments."""
    assert bessel_j0(x) == bessel_j0(-x)
    assert bessel_j1(x) == -bessel_j1(-x)


@pytest.mark.parametrize("bessel_function", [bessel_y0, bessel_y1])
def test_bessel_functions_of_the_second_kind_at_0_and_below(bessel_function):
    """Y0 and Y1 are minus infinity at 0 and NaN for a negative x."""
    assert bessel_function(0.0) == -math.inf
    assert math.isnan(bessel_function(-1.0))
