"""This module holds a formula of Ford (1997).

The formula comes from the row with the key ``5`` in the survey of published test problems.
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


class Ford1997Function5(Formula):
    """This formula comes from Ford (1997).

    The survey writes the source's function as ``exp(x^-1 - 25) - 1``; the formula's intervals are `[0.035, 0.05]`;
    `[0.03, 0.09]`; `[0.025, 0.5]`.

    Printed root: `x* = 0.04`.
    """

    number = (1, 1, 8, 5)
    name = "Function 5"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section “Numerical Tests”, function 5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\frac{1}{\tmp{u}} - 25} - 1",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x**-1 - 25) - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.035, 0.05, 0.015), (0.03, 0.09, 0.06), (0.025, 0.5, 0.475)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.035, "b": 0.05, "c_scale": 0.015}, x=0.0395, c=0.0, expected=0.37225544476214745
        ),
        FormulaTestCase.value(
            params={"a": 0.035, "b": 0.05, "c_scale": 0.015}, x=0.0395, c=0.25, expected=18.53148877277384
        ),
        FormulaTestCase.value(
            params={"a": 0.03, "b": 0.09, "c_scale": 0.06}, x=0.048, c=0.0, expected=-0.9844961464009907
        ),
        FormulaTestCase.value(
            params={"a": 0.025, "b": 0.5, "c_scale": 0.475}, x=0.1675, c=0.0, expected=-0.9999999945619796
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.035, "b": 0.05, "c_scale": 0.015}, expected=(0.035, 0.05)),
        FormulaTestCase.interval_bounds(params={"a": 0.03, "b": 0.09, "c_scale": 0.06}, expected=(0.03, 0.09)),
        FormulaTestCase.interval_bounds(params={"a": 0.025, "b": 0.5, "c_scale": 0.475}, expected=(0.025, 0.5)),
    )
