"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.1#5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Moler2004Function5(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``1/(x - pi)``; the formula's interval is ``[0, 5]``.

    No root: the sign change on `[0, 5]` comes from the pole at `x = pi`.
    """

    number = (1, 4, 3, 13)
    name = "Function 5"
    params = ()
    location_in_publication = "Exercise 4.1, function 5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"\frac{1}{\tmp{u} - \pi}",
        interval="[0, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return 1 / (x - math.pi)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.5, c=0.0, expected=-0.609164519476391),
        FormulaTestCase.value(params={}, x=1.5, c=0.25, expected=-0.3458301772756758),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 5.0)),
    )
