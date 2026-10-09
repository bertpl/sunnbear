"""This module holds the test functions of Chandrupatla's paper, keyed by their number in its Table 1."""

import math


def _paper_function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, and 0 at ``x = 0``."""
    if x == 0.0:
        return 0.0
    else:
        return x * math.exp(-1.0 / (x * x))


def _paper_function_8(x: float) -> float:
    """Return the paper's function 8."""
    xi = 0.61489
    return -3062.0 * (1.0 - xi) * math.exp(-x) / (xi + (1.0 - xi) * math.exp(-x)) - 1013.0 + 1628.0 / x


PAPER_FUNCTIONS = {
    1: lambda x: x**3 - 2.0 * x - 5.0,
    2: lambda x: 1.0 - 1.0 / x**2,
    3: lambda x: (x - 3.0) ** 3,
    4: lambda x: 6.0 * (x - 2.0) ** 5,
    5: lambda x: x**9,
    6: lambda x: x**19,
    7: _paper_function_7,
    8: _paper_function_8,
    9: lambda x: math.exp(x) - 2.0 - 0.01 / x**2 + 0.000002 / x**3,
}
