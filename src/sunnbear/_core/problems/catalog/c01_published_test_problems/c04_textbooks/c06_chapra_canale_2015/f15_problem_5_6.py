"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.6`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem56(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``log(x^2) = 0.7``; the formula's interval is ``[0.5, 2]``.

    The positive real root: graphically, and by 3 iterations each of bisection and false position.
    """

    number = (1, 4, 6, 15)
    name = "Problem 5.6"
    params = ()
    location_in_publication = "Prob. 5.6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\ln{\left(\tmp{u}^{2} \right)} - 0.7",
        interval="[0.5, 2]",
        summary=(
            r"An even function with a logarithmic singularity at $\x = 0$, increasing and concave on the interval, "
            r"which holds the positive one of the function's 2 roots."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return (math.log(x**2)) - (0.7)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.95, c=0.0, expected=-0.8025865887751011),
        FormulaTestCase.value(params={}, x=0.95, c=0.25, expected=-1.8067704763695733),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 2.0)),
    )
