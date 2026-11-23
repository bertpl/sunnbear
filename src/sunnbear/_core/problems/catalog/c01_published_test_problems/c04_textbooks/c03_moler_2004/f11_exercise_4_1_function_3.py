"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.1#3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Moler2004Exercise41Function3(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``log(x + 2/3)``; the formula's interval is ``[0, 1]``.
    """

    number = (1, 4, 3, 11)
    name = "Exercise 4.1, function 3"
    params = ()
    location_in_publication = "Exercise 4.1, function 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\ln{\left(\tmp{u} + \frac{2}{3} \right)}",
        interval="[0, 1]",
        summary="A logarithm, steepest at the lower bound, with 1 simple root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.log(x + 2 / 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.03390155167568136),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.33314444652853825),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
