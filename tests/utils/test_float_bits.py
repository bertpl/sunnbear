"""The 3 measures of `float_bits` count the bits of a value's shortest binary, decimal and rational descriptions."""

import math
from fractions import Fraction

import numpy as np
import pytest

from sunnbear._core.utils.float_bits import n_bits, n_bits_binary, n_bits_decimal, n_bits_rational

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


def test_random_values_hold_close_to_53_bits():
    """Random float64 values in [0.5, 1) score a median of 51 to 54 bits on every measure."""
    # --- arrange ----------------------
    values = 0.5 + 0.5 * np.random.default_rng(0).random(2000)

    # --- act / assert -----------------
    for measure in (n_bits_binary, n_bits_decimal, n_bits_rational):
        assert 51 <= np.median([measure(float(x)) for x in values]) <= 54
