"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006Exercise214(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``1 - log(x)``; the formula's interval is ``(2, 3)``.

    Root `e`; 5 iterations of bisection.
    """

    number = (1, 4, 4, 14)
    name = "Exercise 2.1-4"
    params = ()
    location_in_publication = "Exercise 2.1-4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"1 - \ln{\left(\tmp{u} \right)}",
        interval="[2, 3]",
        summary=r"A decreasing, convex function with 1 root, at $\c$ plus Euler's number.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 1 - math.log(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=0.16709087706489606),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=0.2821602068496833),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
