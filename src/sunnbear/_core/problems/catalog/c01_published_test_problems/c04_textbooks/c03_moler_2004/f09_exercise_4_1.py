"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Moler2004Exercise41(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``sin(x)``; the formula's interval is ``[1, 4]``.
    """

    number = (1, 4, 3, 9)
    name = "Exercise 4.1"
    params = ()
    location_in_publication = "Exercise 4.1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\sin{\left(\tmp{u} \right)}",
        interval="[1, 4]",
        summary=(
            "The sine, which rises to a maximum in the lower 20% of the interval and then falls through 1 simple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return math.sin(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.9, c=0.0, expected=0.9463000876874145),
        FormulaTestCase.value(params={}, x=1.9, c=0.25, expected=0.912763940260521),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 4.0)),
    )
