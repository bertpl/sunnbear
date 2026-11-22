"""This module holds a formula of Chen, Li (2007).

The formula comes from the row with the key ``1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChenLi2007Example1(Formula):
    """This formula comes from Chen, Li (2007).

    The survey writes the source's function as ``log(x)``; the formula's interval is ``[0.5, 5]``.

    The article prints `ln`. `x0 = 5`.
    """

    number = (1, 2, 6, 1)
    name = "Example 1"
    params = ()
    location_in_publication = "Example 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4.5 \c"),),
        expression=r"\ln{\left(\tmp{u} \right)}",
        interval="[0.5, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.5 * c
        return math.log(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.85, c=0.0, expected=0.6151856390902335),
        FormulaTestCase.value(params={}, x=1.85, c=0.25, expected=-0.32158362412746216),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 5.0)),
    )
