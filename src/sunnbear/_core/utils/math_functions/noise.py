"""This module holds noise that is a pure function of x: the same x always gives the same value.

A formula is a pure function of x, c and its parameters, so a published function with random noise takes its noise
from x itself. The noise functions turn x into a 64-bit integer that identifies it, and mix that integer with
splitmix64's finalizer (Sebastiano Vigna, https://prng.di.unimi.it/splitmix64.c), whose output bits each depend on
every input bit; neighboring x-values thus get unrelated noise, spread as independent random draws are.
"""

import math
import re
import warnings

import numba
from numpy import uint64

# With numba's JIT disabled, the mixing runs as numpy scalar arithmetic, which warns on every uint64 overflow;
# splitmix64 relies on that overflow wrapping around modulo 2^64, so the warning reports no error.
warnings.filterwarnings(
    "ignore",
    message=r"overflow encountered in scalar (add|multiply|left_shift)",
    category=RuntimeWarning,
    module=re.escape(__name__) + r"\Z",
)

# _UNIT_SCALE maps the top 53 bits of a mixed integer to a float in [0, 1), each value a multiple of 2^-53
_UNIT_SCALE = 2.0**-53


# ==================================================================================================
#  Noise
# ==================================================================================================
@numba.njit
def uniform_noise(x: float) -> float:
    """Return a value in [0, 1) that depends only on x, distributed as a uniform random draw; NaN for a non-finite x."""
    if not math.isfinite(x):
        return math.nan
    else:
        return _unit_value(_splitmix64(_identifying_integer(x)))


@numba.njit
def normal_noise(x: float) -> float:
    """Return a value that depends only on x, distributed as a standard normal random draw; NaN for a non-finite x.

    The Box-Muller transform turns 2 uniform values into the normal value: the mixed integer of x, and that integer
    mixed once more.
    """
    if not math.isfinite(x):
        return math.nan
    else:
        first = _splitmix64(_identifying_integer(x))
        radius_value = 1.0 - _unit_value(first)  # in (0, 1], so that its log is finite
        angle_value = _unit_value(_splitmix64(first))
        return math.sqrt(-2.0 * math.log(radius_value)) * math.cos(2.0 * math.pi * angle_value)


# ==================================================================================================
#  Helpers
# ==================================================================================================
@numba.njit
def _identifying_integer(x: float) -> uint64:
    """Return a 64-bit integer that identifies a finite x: 2 different values of x give 2 different integers.

    `math.frexp` splits x into a mantissa `m`, with `0.5 <= |m| < 1`, and an exponent `e`; `m*2^53` is an integer of
    at most 54 bits with its sign, and `e` lies between -1073 and 1024.
    """
    mantissa, exponent = math.frexp(x)
    mantissa_bits = uint64(int(mantissa * 2.0**53) + 2**53)  # 0 to 2^54, so it fits 55 bits
    exponent_bits = uint64(exponent + 1100)  # 27 to 2124, so it fits 12 bits
    return mantissa_bits | (exponent_bits << uint64(55))


@numba.njit
def _splitmix64(z: uint64) -> uint64:
    """Return splitmix64's next output for the state `z`: `z` plus its increment, through its finalizer."""
    z = z + uint64(0x9E3779B97F4A7C15)
    z = (z ^ (z >> uint64(30))) * uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> uint64(27))) * uint64(0x94D049BB133111EB)
    return z ^ (z >> uint64(31))


@numba.njit
def _unit_value(z: uint64) -> float:
    """Return the top 53 bits of `z` as a float in [0, 1)."""
    return float(z >> uint64(11)) * _UNIT_SCALE
