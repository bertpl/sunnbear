"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``26–27`` in the survey of published test problems.
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

# MAX_EXP_ARGUMENT is the largest argument for which float64 exp does not overflow.
MAX_EXP_ARGUMENT = math.log(sys.float_info.max)


class RootsFortran2025Case26(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x/exp(1.0/(x*x))`` (x != 0); ``0.0`` (x = 0); the formula's intervals
    are ``[-1, 4]`` (26), ``[-1.1234, 4.4567]`` (27).

    The comment on the root 0 says it is "just almost impossible to get".
    """

    number = (1, 3, 3, 4)
    name = "Case 26"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, cases 26 and 27"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } 709.78 \, \tmp{u}^2 < 1 \\ "
            r"\frac{\tmp{u}}{e^{1/\tmp{u}^2}} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
        notes=(
            r"The expression is 0 where $e^{1/\tmp{u}^2}$ exceeds the largest float64 value, which is about "
            r"$e^{709.78}$.",
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        # where 1/(x*x) exceeds MAX_EXP_ARGUMENT, for abs(x) below about 0.0375, exp overflows and the source's float64
        # value is x/inf = 0; the test `x * x * MAX_EXP_ARGUMENT < 1.0` also holds where x*x underflows to 0
        if x * x * MAX_EXP_ARGUMENT < 1.0:
            return 0.0
        else:
            return x / math.exp(1.0 / (x * x))

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1.0, 4.0, 5.0), (-1.1234, 4.4567, 5.58)),
                summary="The published intervals.",
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.25, expected=-0.12675998655454956
        ),
        FormulaTestCase.value(
            params={"a": -1.1234, "b": 4.4567, "c_scale": 5.58}, x=0.55063, c=0.0, expected=0.020345061698967323
        ),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=1e-200, c=0.0, expected=0.0),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.01, c=0.0, expected=0.0, atol=0.0),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.04, c=0.0, expected=1.4723423419207585e-273, atol=0.0
        ),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(
            params={"a": -1.1234, "b": 4.4567, "c_scale": 5.58}, expected=(-1.1234, 4.4567)
        ),
    )
