"""This module holds a formula of Alefeld, Potra, Shi (1993).

The formula comes from the row with the key ``T5.1-1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class AlefeldPotraShi1993Problem1(Formula):
    """This formula comes from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``sin(x) - x/2``; the formula's interval is ``[pi/2, pi]``.
    """

    number = (1, 2, 4, 1)
    name = "Problem 1"
    params = ()
    location_in_publication = "Table 5.1, problem 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - \frac{\tmp{u}}{2}",
        interval=r"\left[\frac{\pi}{2}, \pi\right]",
        summary=(
            r"A function with 1 simple root, and a slope that triples in magnitude from $\x = \c + \pi/2$ to $\x ="
            r" \c + \pi$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sin(x) - x / 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.5707963267948966, 3.141592653589793)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.04204, c=0.0, expected=-0.13001564370207735),
        FormulaTestCase.value(params={}, x=2.04204, c=0.3925, expected=0.17213131859316824),
        FormulaTestCase.interval_bounds(params={}, expected=(1.5707963267948966, 3.141592653589793)),
    )
