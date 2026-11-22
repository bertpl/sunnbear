"""This module holds a formula of Chen, Li (2006).

The formula comes from the row with the key ``4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChenLi20064(Formula):
    """This formula comes from Chen, Li (2006).

    The survey writes the source's function as ``x*exp(-x) - 0.1``; the formula's interval is ``[0, 1]``.

    `x0 = 1`. Root 0.111833.
    """

    number = (1, 2, 6, 3)
    name = "4"
    params = ()
    location_in_publication = "Example 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} e^{- \tmp{u}} - 0.1",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.exp(-x) - 0.1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.12224546620451536),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.052438528774964306),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
