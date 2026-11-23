"""This module holds a formula of Ford (1997).

The formula comes from the row with the key ``4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Ford1997Function4(Formula):
    """This formula comes from Ford (1997).

    The survey writes the source's function as ``2*x*exp(-20) + 1 - 2*exp(-20*x)``; the formula's intervals are `[0,
    1]`; `[-0.1, 1.5]`; `[-0.5, 2]`.

    Printed root: `x* = 0.034657358821882`. The printed root is not a root of the printed function, whose root is
    `0.034657359020854`: it is the root of `2*exp(-20) + 1 - 2*exp(-20*x)`, the printed function without the factor `x`.
    """

    number = (1, 1, 8, 4)
    name = "Function 4"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section “Numerical Tests”, function 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\frac{2 \tmp{u}}{e^{20}} + 1 - 2 e^{- 20 \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"An increasing function with 1 simple root close to $\x = 0$, within $10^{-4}$ of 1 above $\x = 0.5$, and "
            r"falling steeply below $\x = 0$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 2 * x * math.exp(-20) + 1 - 2 * math.exp(-20 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (-0.1, 1.5, 1.6), (-0.5, 2.0, 2.5)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=0.9950424968833594),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=0.26424111786323057),
        FormulaTestCase.value(params={"a": -0.1, "b": 1.5, "c_scale": 1.6}, x=0.38, c=0.0, expected=0.9989990986995956),
        FormulaTestCase.value(params={"a": -0.5, "b": 2.0, "c_scale": 2.5}, x=0.25, c=0.0, expected=0.9865241070324059),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -0.1, "b": 1.5, "c_scale": 1.6}, expected=(-0.1, 1.5)),
        FormulaTestCase.interval_bounds(params={"a": -0.5, "b": 2.0, "c_scale": 2.5}, expected=(-0.5, 2.0)),
    )
