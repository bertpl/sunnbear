"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-13; 3.11-24`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson20133113(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``exp(-4*x) - 1/10``; the formula's interval is ``[0, 5]``.

    Bisection against regula falsi (3.1-13); regula falsi against the hybrid method, 5 iterations each (3.11-24).
    """

    number = (1, 4, 5, 9)
    name = "3.1-13"
    params = ()
    location_in_publication = "Exercises 3.1-13, 3.11-24"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"e^{- 4 \tmp{u}} - \frac{1}{10}",
        interval="[0, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return math.exp(-4 * x) - 1 / 10

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.5, c=0.0, expected=-0.09752124782333364),
        FormulaTestCase.value(params={}, x=1.5, c=0.25, expected=0.2678794411714423),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 5.0)),
    )
