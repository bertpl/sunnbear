"""The 3 measures of `float_bits` count the bits of a value's shortest binary, decimal and rational descriptions, and
its other functions return values with at least a given number of those bits."""

import math
from fractions import Fraction

import numpy as np
import pytest

from sunnbear._core.utils.float_bits import (
    _simplest_fraction_between,
    draw_floats_with_min_n_bits,
    n_bits,
    n_bits_binary,
    n_bits_decimal,
    n_bits_rational,
    nearest_float_with_min_n_bits,
)

LOG2_10 = math.log2(10)


@pytest.mark.parametrize(
    "x, binary, decimal, rational",
    [
        (0.0, 0.0, 0.0, 0.0),
        (0.5, 1.0, LOG2_10, 1.0),
        (4.0, 1.0, LOG2_10, 2.0),
        (-0.375, 2.0, 3 * LOG2_10, math.log2(3) + 3.0),
        (37 / 1024, 6.0, 9 * LOG2_10, math.log2(37) + 10.0),
        (0.1, 52.0, LOG2_10, math.log2(10)),
        (0.123, 49.0, 3 * LOG2_10, math.log2(123) + math.log2(1000)),
        (1e-5, 53.0, LOG2_10, math.log2(100_000)),
        (1 / 3, 53.0, 16 * LOG2_10, math.log2(3)),
        (2 / 7, 52.0, 16 * LOG2_10, 1.0 + math.log2(7)),
    ],
)
def test_each_measure_counts_the_bits_of_its_shortest_description(x, binary, decimal, rational):
    """Each measure finds the shortest description that reproduces `x`: a dyadic fraction, a decimal or a fraction
    p/q."""
    # --- act / assert -----------------
    assert n_bits_binary(x) == binary
    assert n_bits_decimal(x) == pytest.approx(decimal)
    assert n_bits_rational(x) == pytest.approx(rational)
    assert n_bits(x) == pytest.approx(min(binary, decimal, rational))


@pytest.mark.parametrize("x", [0.25, 5 / 17, 1 / 1024, math.pi / 4, 2.0**-1074, 0.999999])
def test_n_bits_rational_finds_the_fraction_with_the_smallest_denominator_that_rounds_to_x(x):
    """`n_bits_rational` uses the fraction that rounds to `x` and has the smallest denominator; the test checks every
    denominator below 2000."""
    # --- act --------------------------
    bits = n_bits_rational(x)

    # --- assert -----------------------
    q_limit = 2_000
    simplest_fraction = None
    for q in range(1, q_limit):
        candidate = Fraction(round(x * q), q)
        if float(candidate) == x:
            simplest_fraction = candidate
            break
    if simplest_fraction is None:
        # Without a match below q_limit, q is at least q_limit, and for these x the bits then exceed this bound.
        assert bits > 2 * math.log2(q_limit) - 1
    else:
        assert bits == pytest.approx(
            math.log2(max(simplest_fraction.numerator, 1)) + math.log2(simplest_fraction.denominator)
        )


@pytest.mark.parametrize(
    "a, b, c, d, fraction",
    [
        (2, 1, 5, 2, (2, 1)),  # the lower bound is an integer
        (3, 2, 5, 2, (2, 1)),  # an integer lies strictly inside
        (3, 10, 2, 5, (1, 3)),  # no integer inside: 1/3 lies between 0.3 and 0.4
    ],
)
def test_simplest_fraction_between_takes_an_integer_bound_an_inner_integer_or_the_continued_fraction(
    a, b, c, d, fraction
):
    """The simplest fraction in `[a/b, c/d]` is the lower bound when that is an integer, else an integer inside, else
    the fraction that the continued fraction of the bounds gives."""
    # --- act / assert -----------------
    assert _simplest_fraction_between(a, b, c, d) == fraction


def test_random_values_hold_close_to_53_bits():
    """Random float64 values in [0.5, 1) score a median of 51 to 54 bits on every measure."""
    # --- arrange ----------------------
    values = 0.5 + 0.5 * np.random.default_rng(0).random(2000)

    # --- act / assert -----------------
    for measure in (n_bits_binary, n_bits_decimal, n_bits_rational):
        assert 51 <= np.median([measure(float(x)) for x in values]) <= 54


# ==================================================================================================
#  Values with a minimum number of bits
# ==================================================================================================
def test_draw_floats_with_min_n_bits_draws_inside_each_open_interval_with_at_least_min_n_bits():
    """Every value lies strictly inside its own interval, including the interval that starts at 0, and holds at least
    `min_n_bits` bits."""
    # --- arrange ----------------------
    lows = np.repeat([0.0, 0.25, 0.999], 500)
    highs = lows + np.repeat([1 / 1024, 0.5, 0.001], 500)

    # --- act --------------------------
    values = draw_floats_with_min_n_bits(lows, highs, 50, np.random.default_rng(1))

    # --- assert -----------------------
    assert np.all((values > lows) & (values < highs))
    assert min(n_bits(float(value)) for value in values) >= 50


@pytest.mark.parametrize("x", [0.5, 37 / 1024, 0.1, 0.123])
def test_nearest_float_with_min_n_bits_nudges_a_trivial_value_by_a_few_float64_steps(x):
    """A trivial value moves to a value with at least 50 bits, a few float64 steps away, inside the interval."""
    # --- act --------------------------
    nearest = nearest_float_with_min_n_bits(x, 50, x - 0.01, x + 0.01)

    # --- assert -----------------------
    assert nearest is not None
    assert n_bits(nearest) >= 50
    assert 0 < abs(nearest - x) <= 4 * math.ulp(x)


def test_nearest_float_with_min_n_bits_keeps_a_value_that_already_has_them():
    """A value with at least `min_n_bits` bits comes back unchanged."""
    # --- arrange ----------------------
    x = math.pi / 4

    # --- act / assert -----------------
    assert nearest_float_with_min_n_bits(x, 50, 0.0, 1.0) == x


def test_nearest_float_with_min_n_bits_returns_none_when_no_value_inside_the_interval_qualifies():
    """When the open interval holds only the trivial value 0.5, no value qualifies."""
    # --- act / assert -----------------
    assert nearest_float_with_min_n_bits(0.5, 50, math.nextafter(0.5, 0.0), math.nextafter(0.5, 1.0)) is None


def test_draw_floats_with_min_n_bits_draws_again_a_value_on_the_edge_of_its_interval():
    """A random draw of exactly 0 puts a value on the lower edge of its open interval, so it is drawn again."""

    # --- arrange ----------------------
    class _ZeroFirst:
        """`_ZeroFirst` stands in for a random generator whose first `random` call returns only zeros."""

        def __init__(self) -> None:
            """Start the stand-in before its first call."""
            self._rng = np.random.default_rng(2)
            self._is_first_call = True

        def random(self, n: int) -> np.ndarray:
            """Return zeros on the first call, then uniform random values."""
            if self._is_first_call:
                self._is_first_call = False
                return np.zeros(n)
            else:
                return self._rng.random(n)

    lows, highs = np.array([0.25, 0.5]), np.array([0.5, 0.75])

    # --- act --------------------------
    values = draw_floats_with_min_n_bits(lows, highs, 50, _ZeroFirst())  # type: ignore[arg-type]

    # --- assert -----------------------
    assert np.all((values > lows) & (values < highs))
