"""This module holds noise that is a pure function of x: the same x always gives the same value.

A formula is a pure function of x, c and its parameters, so a published function with random noise takes its noise
from x itself. The noise functions mix the 64 bits of x with splitmix64's finalizer (Sebastiano Vigna,
https://prng.di.unimi.it/splitmix64.c), whose output bits each depend on every input bit, so neighboring x-values get
unrelated noise, distributed like independent random draws.
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
        return _unit_value(_splitmix64(_float_bits(x)))


@numba.njit
def normal_noise(x: float) -> float:
    """Return a value that depends only on x, distributed as a standard normal random draw; NaN for a non-finite x.

    The Box-Muller transform turns 2 uniform values into the normal value: the first comes from the mixed integer of x,
    and the second from that integer mixed once more.
    """
    if not math.isfinite(x):
        return math.nan
    else:
        mixed_integer = _splitmix64(_float_bits(x))
        radius_uniform = 1.0 - _unit_value(mixed_integer)  # in (0, 1], so that its log is finite
        angle_uniform = _unit_value(_splitmix64(mixed_integer))
        return math.sqrt(-2.0 * math.log(radius_uniform)) * math.cos(2.0 * math.pi * angle_uniform)


# ==================================================================================================
#  Helpers
# ==================================================================================================
@numba.njit
def _float_bits(x: float) -> uint64:
    """Return the 64 bits of a finite float64 x, as IEEE 754 lays them out: sign, 11 exponent bits, 52 mantissa bits.

    The bits are computed from `math.frexp`, which numba compiles for a scalar, unlike a view of x's memory. `frexp`
    gives `|x| = m*2^e` with `0.5 <= m < 1`; a normal x stores `e + 1022` as its exponent field and the 52 bits after
    the leading 1 of `m`, and a subnormal x stores 0 and `|x|*2^1074`.
    """
    mantissa, exponent = math.frexp(abs(x))
    if x == 0.0:
        exponent_field, mantissa_field = 0, 0
    elif exponent > -1022:
        exponent_field, mantissa_field = exponent + 1022, int(math.ldexp(mantissa, 53)) - 2**52
    else:
        exponent_field, mantissa_field = 0, int(math.ldexp(abs(x), 1074))
    sign_field = 1 if math.copysign(1.0, x) < 0.0 else 0
    return (uint64(sign_field) << uint64(63)) | (uint64(exponent_field) << uint64(52)) | uint64(mantissa_field)


@numba.njit
def _splitmix64(z: uint64) -> uint64:
    """Return splitmix64's next output for the state `z`: `z` plus splitmix64's increment, through its finalizer."""
    z = z + uint64(0x9E3779B97F4A7C15)
    z = (z ^ (z >> uint64(30))) * uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> uint64(27))) * uint64(0x94D049BB133111EB)
    return z ^ (z >> uint64(31))


@numba.njit
def _unit_value(z: uint64) -> float:
    """Return the top 53 bits of `z` as a float in [0, 1)."""
    return float(z >> uint64(11)) * _UNIT_SCALE
