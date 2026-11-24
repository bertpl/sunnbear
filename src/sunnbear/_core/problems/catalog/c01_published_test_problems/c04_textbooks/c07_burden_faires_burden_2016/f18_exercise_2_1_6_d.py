"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-6(d); 2.3-12(b)`` in the survey of published test problems.
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


class BurdenFairesBurden2016Exercise216D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x + 1 - 2*sin(pi*x)``; the formula's intervals are `[0, 0.5]`; `[0.5,
    1]`.

    As 2.1-6(c).
    """

    number = (1, 4, 7, 18)
    name = "Exercise 2.1-6(d)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercises 2.1-6(d), 2.3-12(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u} + 1 - 2 \sin{\left(\pi \tmp{u} \right)}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function with 1 simple root per interval and a minimum of $-0.53$ about midway between those 2 roots."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x + 1 - 2 * math.sin(math.pi * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((0.0, 0.5, 0.5), (0.5, 1.0, 0.5)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 0.5, "c_scale": 0.5}, x=0.15, c=0.0, expected=0.24201900052090644),
        FormulaTestCase.value(params={"a": 0.0, "b": 0.5, "c_scale": 0.5}, x=0.15, c=0.25, expected=0.8680818085443102),
        FormulaTestCase.value(
            params={"a": 0.5, "b": 1.0, "c_scale": 0.5}, x=0.65, c=0.0, expected=-0.13201304837673564
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 0.5, "c_scale": 0.5}, expected=(0.0, 0.5)),
        FormulaTestCase.interval_bounds(params={"a": 0.5, "b": 1.0, "c_scale": 0.5}, expected=(0.5, 1.0)),
    )
