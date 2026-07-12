"""Example formulas: minimal worked instances of the `Formula` surface.

Two deliberately simple polynomial families that exercise the framework's
parameter layering — ``p`` shapes a function's character, ``c`` only shifts
the root — and both compilation paths (numba-jitted and plain Python). They
double as test fixtures; the real formula corpus is built as separate modules
following the same pattern.
"""

from typing import cast

import numba

from ._formula import Formula, XCFun
from ._recipes import ParamRecipe


# ==================================================================================================
#  f101 — cubic
# ==================================================================================================
def _make_cubic(p1: float) -> XCFun:
    """Build the jitted cubic ``x^3 - p1*x - c`` (compilation deferred to first call)."""

    @numba.njit
    def f(x: float, c: float) -> float:
        return x * x * x - p1 * x - c

    # the numba dispatcher is call-compatible with the plain signature it wraps
    return cast("XCFun", f)


CUBIC = Formula(
    number=101,
    name="poly_cubic",
    make=_make_cubic,
    bracket=lambda p1: (-2.0, 2.0),
    param_names=("p1",),
    recipes=(ParamRecipe.linear("p1", 0.0, 1.0, step=0.2),),
)


# ==================================================================================================
#  f102 — odd power (difficulty knob)
# ==================================================================================================
def _make_odd_power(p1: float) -> XCFun:
    """Build the plain-Python ``x^p1 - c`` for odd integer ``p1``.

    Higher powers flatten the function around the root at ``c = 0``,
    turning a benign polynomial into a derivative-zero stress case.
    """

    def f(x: float, c: float) -> float:
        """Evaluate ``x^p1 - c``."""
        return x**p1 - c

    return f


def _odd_power_params_valid(p1: float) -> bool:
    """Require an odd integer power (even powers break the sign change across the bracket)."""
    return p1 == int(p1) and int(p1) % 2 == 1


ODD_POWER = Formula(
    number=102,
    name="poly_odd_power",
    make=_make_odd_power,
    bracket=lambda p1: (-2.0, 2.0),
    param_names=("p1",),
    recipes=(ParamRecipe.linear("p1", 1.0, 7.0, step=2.0),),
    is_param_tuple_valid=_odd_power_params_valid,
)


FORMULAS: tuple[Formula, ...] = (CUBIC, ODD_POWER)
