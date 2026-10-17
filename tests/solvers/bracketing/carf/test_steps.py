"""These tests assert that the individual steps of `CARF` follow its algorithm, and that its quadratic step finds the
quadratic's zero at any scale of ``f`` and with ``t`` on or near an interval bound."""

import math

import mpmath
import pytest

from sunnbear.solvers import CARF
from tests.solvers.example_functions import cubic, steep_exponential

# The 3 points ``(a, f(a))``, ``(t, f(t))`` and ``(b, f(b))`` of a quadratic step of `CARF` on ``x^19`` over
# ``[-1, 4]``, at the benchmark's smallest allowed ``xtol``: ``t`` lies within rounding error of ``b``, with
# ``f(t) = f(b)``, and the function values are below 1e-180.
_X19_STEP = (
    -1.1602778377907523e-10,
    6.2640603329516776e-12,
    6.264060332951684e-12,
    -1.6853027997042577e-189,
    1.381219523405383e-213,
    1.38121952340541e-213,
)


@pytest.mark.parametrize(
    "f, a, b, first_x",
    [(cubic, 1.0, 2.0, 1.0 + 1.0 / 6.0), (steep_exponential, 0.0, 1.0, 0.1)],
    ids=["chord_zero_inside", "chord_zero_clipped"],
)
def test_the_first_x_value_is_the_chord_zero_clipped_into_the_middle_80_percent(f, a, b, first_x):
    """The first x-value is the chord's zero, kept when it lies in the middle 80 % of the interval and clipped to its
    edge otherwise."""
    # --- act --------------------------
    result = CARF().solve(f, a, b, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(first_x, abs=1e-15)


def test_the_quadratic_zero_is_found_with_t_within_rounding_error_of_a_bound():
    """At the quadratic step of `_X19_STEP`, the quadratic's zero agrees with its value in 50-digit arithmetic."""
    # --- act --------------------------
    zero = CARF._quadratic_zero(*_X19_STEP)

    # --- assert -----------------------
    assert zero == pytest.approx(_exact_quadratic_zero(*_X19_STEP), rel=1e-14)


@pytest.mark.parametrize("scale", [2.0**-1000, 1.0, 2.0**1000], ids=["2^-1000", "1", "2^1000"])
def test_the_quadratic_zero_does_not_depend_on_the_scale_of_f(scale):
    """The quadratic through ``(0, -2)``, ``(0.75, 0.75^2 - 2)`` and ``(2, 2)`` is ``x^2 - 2``; with its function values
    scaled by a power of 2 from 2^-1000 to 2^1000, its zero is ``sqrt(2)``, to within 1 ulp."""
    # --- act --------------------------
    zero = CARF._quadratic_zero(0.0, 0.75, 2.0, -2.0 * scale, (0.75**2 - 2.0) * scale, 2.0 * scale)

    # --- assert -----------------------
    assert zero == pytest.approx(math.sqrt(2.0), abs=math.ulp(math.sqrt(2.0)))


@pytest.mark.parametrize("t, ft", [(0.0, -2.0), (2.0, 2.0)], ids=["t_on_a", "t_on_b"])
def test_the_quadratic_zero_with_t_on_a_bound_is_the_chord_zero(t, ft):
    """With ``t`` on an interval bound, the quadratic is not defined, and the step returns the zero of the chord
    through ``(0, -2)`` and ``(2, 2)``, which is 1."""
    # --- act --------------------------
    zero = CARF._quadratic_zero(0.0, t, 2.0, -2.0, ft, 2.0)

    # --- assert -----------------------
    assert zero == 1.0


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _exact_quadratic_zero(a: float, t: float, b: float, fa: float, ft: float, fb: float) -> float:
    """Return the zero in ``[a, b]`` of the quadratic through ``(a, fa)``, ``(t, ft)`` and ``(b, fb)``, computed in
    50-digit arithmetic."""
    with mpmath.workdps(50):
        a, t, b, fa, ft, fb = (mpmath.mpf(value) for value in (a, t, b, fa, ft, fb))
        slope_a_t = (ft - fa) / (t - a)
        slope_t_b = (fb - ft) / (b - t)
        c2 = (slope_t_b - slope_a_t) / (b - a)
        # The quadratic fa + slope_a_t * (x - a) + c2 * (x - a) * (x - t), as c2 * x^2 + c1 * x + c0.
        c1 = slope_a_t - c2 * (a + t)
        c0 = fa - slope_a_t * a + c2 * a * t
        sqrt_discriminant = mpmath.sqrt(c1 * c1 - 4 * c2 * c0)
        zeros = [(-c1 + sqrt_discriminant) / (2 * c2), (-c1 - sqrt_discriminant) / (2 * c2)]
        return float(next(zero for zero in zeros if a <= zero <= b))
