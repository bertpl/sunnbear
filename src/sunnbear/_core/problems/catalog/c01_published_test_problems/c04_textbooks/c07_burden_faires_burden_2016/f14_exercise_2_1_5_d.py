"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-5(d)`` in the survey of published test problems.
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


class BurdenFairesBurden2016Exercise215D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x*cos(x) - 2*x^2 + 3*x - 1``; the formula's intervals are `[0.2, 0.3]`;
    `[1.2, 1.3]`.

    As 2.1-5(b).
    """

    number = (1, 4, 7, 14)
    name = "Exercise 2.1-5(d)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercise 2.1-5(d)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u} \cos{\left(\tmp{u} \right)} - 2 \tmp{u}^{2} + 3 \tmp{u} - 1",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function positive between its 2 simple roots, 1 on each interval, with the lower root close to the upper"
            " bound of $[0.2, 0.3]$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x * math.cos(x) - 2 * x**2 + 3 * x - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((0.2, 0.3, 0.1), (1.2, 1.3, 0.1)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.2, "b": 0.3, "c_scale": 0.1}, x=0.23, c=0.0, expected=-0.19185672914876375
        ),
        FormulaTestCase.value(
            params={"a": 0.2, "b": 0.3, "c_scale": 0.1}, x=0.23, c=0.25, expected=-0.2683424981735014
        ),
        FormulaTestCase.value(params={"a": 1.2, "b": 1.3, "c_scale": 0.1}, x=1.23, c=0.0, expected=0.07531240436313824),
        FormulaTestCase.interval_bounds(params={"a": 0.2, "b": 0.3, "c_scale": 0.1}, expected=(0.2, 0.3)),
        FormulaTestCase.interval_bounds(params={"a": 1.2, "b": 1.3, "c_scale": 0.1}, expected=(1.2, 1.3)),
    )
