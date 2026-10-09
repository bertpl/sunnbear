"""This module holds the test functions of Chandrupatla's paper, keyed by their number in its Table 1.

Function 7 comes in 2 versions: as the paper prints it, in `CHANDRUPATLA_FUNCTIONS`, and as the paper's BASIC listing
computes it, in `CHANDRUPATLA_LISTING_FUNCTIONS`.
"""

import math


def _function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, and 0 at ``x = 0``."""
    if x == 0.0:
        return 0.0
    else:
        return x * math.exp(-1.0 / (x * x))


def _listing_function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, set to 0 where ``|x| < 3.8e-4``, as the paper's BASIC
    listing does."""
    if abs(x) < 3.8e-4:
        return 0.0
    else:
        return x * math.exp(-(x**-2))


def _function_8(x: float) -> float:
    """Return the paper's function 8."""
    xi = 0.61489
    return -3062.0 * (1.0 - xi) * math.exp(-x) / (xi + (1.0 - xi) * math.exp(-x)) - 1013.0 + 1628.0 / x


CHANDRUPATLA_FUNCTIONS = {
    1: lambda x: x**3 - 2.0 * x - 5.0,
    2: lambda x: 1.0 - 1.0 / x**2,
    3: lambda x: (x - 3.0) ** 3,
    4: lambda x: 6.0 * (x - 2.0) ** 5,
    5: lambda x: x**9,
    6: lambda x: x**19,
    7: _function_7,
    8: _function_8,
    9: lambda x: math.exp(x) - 2.0 - 0.01 / x**2 + 0.000002 / x**3,
}

CHANDRUPATLA_LISTING_FUNCTIONS = {**CHANDRUPATLA_FUNCTIONS, 7: _listing_function_7}
