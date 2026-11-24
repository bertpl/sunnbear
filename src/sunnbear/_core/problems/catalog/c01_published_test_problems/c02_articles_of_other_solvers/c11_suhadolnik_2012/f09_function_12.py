"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``12`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function12(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``exp(x) - 2*x - 1``; the formula's interval is ``[.2, 3]``.
    """

    number = (1, 2, 11, 9)
    name = "Function 12"
    params = ()
    location_in_publication = "Table 1, function 12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.8 \c"),),
        expression=r"e^{\tmp{u}} - 2 \tmp{u} - 1",
        interval="[0.2, 3]",
        summary="A convex function with 2 roots 1.26 apart, only the upper of which lies on the interval.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.8 * c
        return math.exp(x) - 2 * x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.2, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.04, c=0.0, expected=-0.2507829856484404),
        FormulaTestCase.value(params={}, x=1.04, c=0.25, expected=-0.27505240943640624),
        FormulaTestCase.interval_bounds(params={}, expected=(0.2, 3.0)),
    )
