"""This module holds formula f1.99.3.3.4, the modified version of the published formula f1.3.3.4.

A change of formula f1.3.3.4 may need a matching change of this module.
"""

import math
import sys

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE

# MAX_EXP_ARGUMENT is the largest argument for which float64 exp does not overflow.
MAX_EXP_ARGUMENT = math.log(sys.float_info.max)


class ModifiedRootsFortran2025Case26(Formula):
    """This formula is the modified version of formula f1.3.3.4, from roots-fortran (2025).

    The survey writes the source's function as ``x/exp(1.0/(x*x))`` (x != 0); ``0.0`` (x = 0); the published intervals
    are ``[-1, 4]`` (26), ``[-1.1234, 4.4567]`` (27).

    The comment on the root 0 says it is "just almost impossible to get".

    The formula adds ``TINY_LINEAR_TERM_SLOPE*x`` to the published function, on the published intervals; ``c`` shifts x
    by the rule of category 1, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is about 4.5e-277.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    In float64, the published function is exactly 0 within about 0.04 of the root, because its true values there lie
    below float64's range; no way of writing the function avoids these exact zeros.

    With the term, f is exactly 0 only within about 5e-48 of the root, where the term underflows too; beyond about 0.04
    from the root, the term changes f by less than the rounding error of f.

    The modification changes what the test problem tests: with the published function, a solver may stop at any
    x-value within about 0.04 of the root, while with the term a solver must locate the root, near which f is the
    linear term.
    """

    number = (1, 99, 3, 3, 4)
    name = "Case 26"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, cases 26 and 27"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - \param{c_scale} \c"),
            (
                r"\fn{g}(\x)",
                (
                    r"\begin{cases} 0 & \text{if } 709.78 \, \x^2 < 1 \\ \frac{\x}{e^{1/\x^2}} & "
                    r"\text{otherwise} \end{cases}"
                ),
            ),
        ),
        expression=r"\fn{g}(\tmp{u}) + 2^{-918} \, \tmp{u}",
        interval=r"[\param{a}, \param{b}]",
        notes=(
            (
                r"$\fn{g}(\x)$ is 0 where $e^{1/\x^2}$ exceeds the largest float64 value, which is about "
                "$e^{709.78}$."
            ),
            (
                r"The term $2^{-918} \, \tmp{u}$ keeps the function from being exactly 0 within about 0.04 "
                r"of its root, where the published function, $\fn{g}(\tmp{u})$, underflows to 0 in "
                "float64. This changes what the test problem tests: with the published function, a solver "
                "may stop at any x-value within about 0.04 of the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, and add ``TINY_LINEAR_TERM_SLOPE*y``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        # where 1/(x*x) exceeds MAX_EXP_ARGUMENT, for abs(x) below about 0.0375, exp overflows and the source's float64
        # value is x/inf = 0; the test `x * x * MAX_EXP_ARGUMENT < 1.0` also holds where x*x underflows to 0
        if x * x * MAX_EXP_ARGUMENT < 1.0:
            published_value = 0.0
        else:
            published_value = x / math.exp(1.0 / (x * x))
        return published_value + TINY_LINEAR_TERM_SLOPE * x

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (-1.0, 4.0, 5.0),
                    (-1.1234, 4.4567, 5.58),
                ),
                summary="The published intervals.",
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.25, expected=-0.12675998655454956
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.01, c=0.0, expected=4.512985939662074e-279, atol=0.0
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.1234, "b": 4.4567, "c_scale": 5.58}, expected=(-1.1234, 4.4567)
        ),
        FormulaTestCase.value(
            params={"a": -1.1234, "b": 4.4567, "c_scale": 5.58},
            x=0.01,
            c=0.0,
            expected=4.512985939662074e-279,
            atol=0.0,
        ),
    )
