"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-2, 2.3-4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise232(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``-x^3 - cos(x)``; the formula's interval is `[-1, 0]` (false position,
    2.3-4).

    Newton from `p0 = -1` to `p2`, and whether `p0 = 0` could be used (2.3-2); secant and false position from `p0 = -1,
    p1 = 0` to `p3` (2.3-4).
    """

    number = (1, 4, 7, 30)
    name = "Exercise 2.3-2"
    params = ()
    location_in_publication = "Exercises 2.3-2, 2.3-4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"- \tmp{u}^{3} - \cos{\left(\tmp{u} \right)}",
        interval="[-1, 0]",
        summary=(
            "A decreasing function with 1 simple root in the lower 15% of the interval and a slope of 0 at the upper "
            "bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return -(x**3) - math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.7, c=0.0, expected=-0.4218421872844885),
        FormulaTestCase.value(params={}, x=-0.7, c=0.25, expected=0.27569191053611636),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 0.0)),
    )
