"""This module measures how many bits of information a float64 value holds, in 3 representations.

A value is trivial when a short description reproduces it exactly: a few binary digits, a few decimal digits, or a
fraction with a small numerator and denominator. A test function treated as a black box can behave differently at such
a value; for example, `sin(100·π·x + c)` has a zero at exactly `x = 0` for a round enough `c`. Each function returns the
length of the shortest such description in bits, as a float; a random float64 value scores about 51 to 53 bits in each
representation, and a trivial value far less:

- `n_bits_binary`: the significant bits, the bit length of the odd integer `m` in `|x| = m · 2^e`;
- `n_bits_decimal`: the significant digits of the shortest decimal that rounds back to `x`, times log2(10);
- `n_bits_rational`: log2(p) + log2(q) for the simplest fraction p/q that rounds to `|x|`;
- `n_bits`: the smallest of the 3.

Multiples of constants such as π or e are not measured: there are too many such constants. Each function takes a finite
value, and returns 0 for 0.
"""

import math

LOG2_10 = math.log2(10)


# ==================================================================================================
#  Measures
# ==================================================================================================
def n_bits_binary(x: float) -> float:
    """Return the number of significant bits of `x`, the bit length of the odd integer `m` in `|x| = m · 2^e`."""
    return float(abs(x.as_integer_ratio()[0]).bit_length())


def n_bits_decimal(x: float) -> float:
    """Return the significant digits of the shortest decimal that rounds back to `x`, times log2(10).

    Python's `repr` of a float is that shortest decimal, so its digits without the leading and trailing zeros, the sign
    and the exponent are the significant digits.
    """
    digits = repr(abs(x)).split("e")[0].replace(".", "").strip("0")
    return len(digits) * LOG2_10


def n_bits_rational(x: float) -> float:
    """Return log2(p) + log2(q) for the simplest fraction p/q that rounds to `|x|`, the one with the smallest q.

    The fraction rounds to `|x|` when it lies between the midpoints to the 2 float64 neighbors of `|x|`; both midpoints
    count as inside, whichever way a tie would round.
    """
    x = abs(x)
    if x == 0:
        return 0.0
    else:
        p, q = _simplest_fraction_between(*_rounding_interval(x))
        return math.log2(p) + math.log2(q)


def n_bits(x: float) -> float:
    """Return the smallest of `n_bits_binary`, `n_bits_decimal` and `n_bits_rational`: the bits that `x` holds."""
    return min(n_bits_binary(x), n_bits_decimal(x), n_bits_rational(x))


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _rounding_interval(x: float) -> tuple[int, int, int, int]:
    """Return the interval of reals that round to the positive `x`, as the fractions `a/b` and `c/d`.

    Its bounds are the midpoints between `x` and its 2 float64 neighbors. All 3 values are dyadic fractions, so the
    bounds are exact over a common power-of-2 denominator.
    """
    ratios = [value.as_integer_ratio() for value in (math.nextafter(x, 0.0), x, math.nextafter(x, math.inf))]
    denominator = max(den for _, den in ratios)
    below, at, above = (num * (denominator // den) for num, den in ratios)
    return below + at, 2 * denominator, at + above, 2 * denominator


def _simplest_fraction_between(a: int, b: int, c: int, d: int) -> tuple[int, int]:
    """Return the fraction p/q with the smallest q, then the smallest p, such that `a/b <= p/q <= c/d`.

    It follows the continued fraction of the 2 bounds: an integer in the interval is the answer; otherwise both bounds
    share their integer part `n`, and the answer is `n + 1/y` for the simplest `y` between the reciprocals of the
    bounds' fractional parts. `0 <= a/b < c/d` is required.
    """
    n = a // b
    if n * b == a:
        return n, 1
    elif (n + 1) * d <= c:
        return n + 1, 1
    else:
        p, q = _simplest_fraction_between(d, c - n * d, b, a - n * b)
        return n * p + q, p
