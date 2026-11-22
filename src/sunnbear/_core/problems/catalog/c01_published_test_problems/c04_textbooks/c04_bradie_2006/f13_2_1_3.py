"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-3; 2.2-8; 2.4-9; 2.5-9`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006213(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``sin(x)``; the formula's interval is ``(3, 4)``.

    Root `pi`. Bisection (2.1-3), false position (2.2-8), Newton from `p0 = 4` (2.4-9) and secant from `p0 = 3, p1 = 4`
    (2.5-9); the last 3 ask for the apparent order of convergence.
    """

    number = (1, 4, 4, 13)
    name = "2.1-3"
    params = ()
    location_in_publication = "Exercises 2.1-3, 2.2-8, 2.4-9, 2.5-9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sin{\left(\tmp{u} \right)}",
        interval="[3, 4]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sin(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.3, c=0.0, expected=-0.1577456941432482),
        FormulaTestCase.value(params={}, x=3.3, c=0.25, expected=0.0914646422324372),
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 4.0)),
    )
