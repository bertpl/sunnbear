"""This module measures how many bits of information a float64 value holds, in 3 representations.

A value is trivial when a short description reproduces it exactly: a few binary digits, a few decimal digits, or a
fraction with a small numerator and denominator.

Each measure returns the length of the shortest such description in bits. A random float64 value scores
about 51 to 54 bits in each representation, and a trivial value far less:

- `n_bits_binary`: the binary description;
- `n_bits_decimal`: the decimal description;
- `n_bits_rational`: the rational description;
- `n_bits`: the smallest of the 3.

A multiple of a constant such as π or e does not count as trivial, because there are too many such constants to check.
Each measure takes a finite value, and returns 0 for 0.

`draw_floats_with_min_n_bits` draws values with a given minimum of `n_bits` at random in given intervals.
"""

import math

import numpy as np

LOG2_10 = math.log2(10)


# ==================================================================================================
#  Measures
# ==================================================================================================
def n_bits_binary(x: float) -> float:
    """Return the number of significant bits of `x`, the bit length of the odd integer `m` in `|x| = m · 2^e`.

    `x` must be finite.
    """
    m = abs(x.as_integer_ratio()[0])
    if m > 0:
        # The numerator of an even integer still has trailing zero bits; shifting them out leaves the odd `m`.
        m >>= (m & -m).bit_length() - 1
    return float(m.bit_length())


def n_bits_decimal(x: float) -> float:
    """Return the number of significant digits of the shortest decimal that rounds back to `x`, times log2(10).

    `x` must be finite.
    """
    # Python's repr of a float is the shortest decimal that rounds back to the float; without the sign, the exponent,
    # the point and the leading and trailing zeros, its digits are the significant digits.
    digits = repr(abs(x)).split("e")[0].replace(".", "").strip("0")
    return len(digits) * LOG2_10


def n_bits_rational(x: float) -> float:
    """Return log2(p) + log2(q) for the fraction p/q that rounds to `|x|` and has the smallest q.

    The fraction rounds to `|x|` when it lies between the midpoints between `|x|` and its 2 float64 neighbors; both
    midpoints count as inside, whichever way a tie would round. `x` must be finite.
    """
    x = abs(x)
    if x == 0:
        return 0.0
    else:
        p, q = _simplest_fraction_between(*_rounding_interval(x))
        return math.log2(p) + math.log2(q)


def n_bits(x: float) -> float:
    """Return the smallest of `n_bits_binary`, `n_bits_decimal` and `n_bits_rational`: the bits of information of `x`.

    `x` must be finite.
    """
    return min(n_bits_binary(x), n_bits_decimal(x), n_bits_rational(x))


# ==================================================================================================
#  Values with a minimum number of bits
# ==================================================================================================
def draw_floats_with_min_n_bits(
    lows: np.ndarray, highs: np.ndarray, min_n_bits: float, rng: np.random.Generator
) -> np.ndarray:
    """Return 1 uniform random value in each open interval `(lows[i], highs[i])` with at least `min_n_bits` bits.

    A value on an edge of its open interval (from a random draw of exactly 0, or from rounding), or with fewer than
    `min_n_bits` bits, is drawn again until it fits, so the call never returns if an interval holds no such value. At
    50 bits, about 1 draw in 4 to 7 is drawn again.
    """
    values = np.empty(lows.size)
    needs_draw = np.ones(lows.size, dtype=bool)
    while needs_draw.any():
        indices = np.flatnonzero(needs_draw)
        values[indices] = lows[indices] + (highs[indices] - lows[indices]) * rng.random(indices.size)
        for i in indices.tolist():
            if lows[i] < values[i] < highs[i]:
                needs_draw[i] = n_bits(float(values[i])) < min_n_bits
            else:
                needs_draw[i] = True
    return values


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _rounding_interval(x: float) -> tuple[int, int, int, int]:
    """Return the interval of reals that round to the positive `x`, as the fractions `a/b` and `c/d`.

    The interval's bounds are the midpoints between `x` and its 2 float64 neighbors. `x` and its 2 float64 neighbors are
    dyadic fractions, so the bounds are exact over a common power-of-2 denominator. The bounds are computed on
    integers, because `fractions.Fraction` arithmetic makes `n_bits_rational` about 3 times slower.
    """
    ratios = [value.as_integer_ratio() for value in (math.nextafter(x, 0.0), x, math.nextafter(x, math.inf))]
    denominator = max(den for _, den in ratios)
    below_numerator, at_numerator, above_numerator = (num * (denominator // den) for num, den in ratios)
    return below_numerator + at_numerator, 2 * denominator, at_numerator + above_numerator, 2 * denominator


def _simplest_fraction_between(a: int, b: int, c: int, d: int) -> tuple[int, int]:
    """Return the fraction p/q with the smallest q, then the smallest p, such that `a/b <= p/q <= c/d`.

    The search follows the continued fraction of the 2 bounds:

    - if the interval holds an integer, the smallest such integer is the answer;
    - otherwise both bounds share their integer part `n`, and the answer is `n + 1/y`, where `y` is the simplest
      fraction between the reciprocals of the bounds' fractional parts.

    `0 <= a/b < c/d` is required.
    """
    n = a // b
    if n * b == a:
        return n, 1
    elif (n + 1) * d <= c:
        return n + 1, 1
    else:
        p, q = _simplest_fraction_between(d, c - n * d, b, a - n * b)
        return n * p + q, p
