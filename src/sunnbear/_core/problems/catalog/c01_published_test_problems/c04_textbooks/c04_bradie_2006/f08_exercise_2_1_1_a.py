"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-1(a); 2.2-1(a); 2.4-1(a); 2.5-1(a)`` in the survey of published test
problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006Exercise211A(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``log(1 + x) - cos(x)``; the formula's interval is ``(0, 1)``.

    Bisection and false position to `p3` (2.1-1, 2.2-1), Newton and secant to `p4` (2.4-1, 2.5-1).
    """

    number = (1, 4, 4, 8)
    name = "Exercise 2.1-1(a)"
    params = ()
    location_in_publication = "Exercises 2.1-1(a), 2.2-1(a), 2.4-1(a), 2.5-1(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\ln{\left(1 + \tmp{u} \right)} - \cos{\left(\tmp{u} \right)}",
        interval="[0, 1]",
        summary="An increasing function with 1 simple root on the interval, where the slope stays between 1 and 1.5.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.log(1 + x) - math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.692972224658115),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.9499600962255342),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
