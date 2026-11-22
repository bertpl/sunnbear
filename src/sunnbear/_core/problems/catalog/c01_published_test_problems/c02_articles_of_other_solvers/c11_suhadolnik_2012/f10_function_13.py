"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``13`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function13(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``exp(-x) - x - sin(x)``; the formula's interval is ``[0, .5]``.
    """

    number = (1, 2, 11, 10)
    name = "Function 13"
    params = ()
    location_in_publication = "Table 1, function 13"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.5 \c"),),
        expression=r"e^{- \tmp{u}} - \tmp{u} - \sin{\left(\tmp{u} \right)}",
        interval="[0, 0.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.5 * c
        return math.exp(-x) - x - math.sin(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.15, c=0.0, expected=0.5612698439514586),
        FormulaTestCase.value(params={}, x=0.15, c=0.25, expected=0.9253125161136203),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 0.5)),
    )
