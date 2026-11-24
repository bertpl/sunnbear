"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-14`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise2314(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``tan(pi*x) - 6``; the formula's interval is ``[0, 0.48]``.

    Zero `(1/pi)*arctan(6) = 0.447431543`. 10 iterations each of bisection, false position and secant from `p0 = 0, p1 =
    0.48`; asks which works best, and why.
    """

    number = (1, 4, 7, 40)
    name = "Exercise 2.3-14"
    params = ()
    location_in_publication = "Exercise 2.3-14"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.48 \c"),),
        expression=r"\tan{\left(\pi \tmp{u} \right)} - 6",
        interval="[0, 0.48]",
        summary=(
            "An increasing tangent with 1 simple root only 0.053 below the tangent's pole, which lies above the upper "
            "bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.48 * c
        return math.tan(math.pi * x) - 6

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.48)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.144, c=0.0, expected=-5.513994647140799),
        FormulaTestCase.value(params={}, x=0.144, c=0.25, expected=-5.924458573745623),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 0.48)),
    )
