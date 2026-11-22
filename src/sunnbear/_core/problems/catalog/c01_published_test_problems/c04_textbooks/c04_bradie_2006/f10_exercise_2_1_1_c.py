"""This module holds a formula of Bradie (2006).

The formula comes from the rows with the keys ``2.1-1(c); 2.2-1(c); 2.4-1(c); 2.5-1(c)`` and ``Fig. 2.7; Ex. 2.6, 2.7,
2.14, 2.15`` in the survey of published test problems.
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


class Bradie2006Exercise211C(Formula):
    """This formula comes from Bradie (2006).

    The source prints 1 function in 2 rows, each on its own interval:

    - 2.1-1(c); 2.2-1(c); 2.4-1(c); 2.5-1(c): ``exp(-x) - x``; the formula's interval is ``(0, 1)``
    - Fig. 2.7; Ex. 2.6, 2.7, 2.14, 2.15: ``x = exp(-x)``; the formula's interval is `[-2, 5]` (Fig. 2.7)

    2.1-1(c); 2.2-1(c); 2.4-1(c); 2.5-1(c): As 2.1-1(a). Its root is the fixed point of `x = exp(-x)` (Ex. 2.6).

    Fig. 2.7; Ex. 2.6, 2.7, 2.14, 2.15: Fixed point `0.5671432904`. Fixed-point iteration from `p0 = 0` (Ex. 2.6), with
    the error estimate, reaching `p21 = 0.5671477143` at tolerance `5E-6` (Ex. 2.7); Aitken extrapolation (Ex. 2.14) and
    Steffensen, whose `p3 = 0.5671432948` (Ex. 2.15). Figure 2.7 plots it on `[-2, 5]`.
    """

    number = (1, 4, 4, 10)
    name = "Exercise 2.1-1(c)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = (
        "Exercises 2.1-1(c), 2.2-1(c), 2.4-1(c), 2.5-1(c); Fig. 2.7; Examples 2.6, 2.7, 2.14, 2.15"
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{- \tmp{u}} - \tmp{u}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(-x) - x

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (-2.0, 5.0, 7.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=0.4408182206817179),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=0.9012294245007141),
        FormulaTestCase.value(params={"a": -2.0, "b": 5.0, "c_scale": 7.0}, x=0.1, c=0.0, expected=0.8048374180359595),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 5.0, "c_scale": 7.0}, expected=(-2.0, 5.0)),
    )
