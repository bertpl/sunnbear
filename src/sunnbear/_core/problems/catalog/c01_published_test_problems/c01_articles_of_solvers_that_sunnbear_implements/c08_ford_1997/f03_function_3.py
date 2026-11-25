"""This module holds a formula of Ford (1997).

The formula comes from the row with the key ``3`` in the survey of published test problems.
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


class Ford1997Function3(Formula):
    """This formula comes from Ford (1997).

    The survey writes the source's function as ``exp(21000/x)/(1.11*10^11*x^2) - 1``; the formula's intervals are `[550,
    560]`; `[400, 600]`; `[350, 850]`.

    Printed root: `x* = 551.77382493033`. The article prints the constant as `21,000`.
    """

    number = (1, 1, 8, 3)
    name = "Function 3"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section “Numerical Tests”, function 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\frac{e^{\frac{21000}{\tmp{u}}}}{1.11 \cdot 10^{11} \tmp{u}^{2}} - 1",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A decreasing function with 1 root, above $6 \cdot 10^{9}$ at 200 below that root and within $10^{-3}$ of "
            r"$-1$ from 115 above that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(21000 / x) / (1.11 * 10**11 * x**2) - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((550.0, 560.0, 10.0), (400.0, 600.0, 100.0), (350.0, 850.0, 1000.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 550.0, "b": 560.0, "c_scale": 10.0}, x=553.0, c=0.0, expected=-0.08499751420971996
        ),
        FormulaTestCase.value(
            params={"a": 550.0, "b": 560.0, "c_scale": 10.0}, x=553.0, c=0.25, expected=0.09712049308920227
        ),
        FormulaTestCase.value(
            params={"a": 400.0, "b": 600.0, "c_scale": 100.0}, x=460.0, c=0.0, expected=2854.279157641333
        ),
        FormulaTestCase.value(
            params={"a": 350.0, "b": 850.0, "c_scale": 1000.0}, x=500.0, c=0.0, expected=61.676574469207246
        ),
        FormulaTestCase.interval_bounds(params={"a": 550.0, "b": 560.0, "c_scale": 10.0}, expected=(550.0, 560.0)),
        FormulaTestCase.interval_bounds(params={"a": 400.0, "b": 600.0, "c_scale": 100.0}, expected=(400.0, 600.0)),
        FormulaTestCase.interval_bounds(params={"a": 350.0, "b": 850.0, "c_scale": 1000.0}, expected=(350.0, 850.0)),
    )
