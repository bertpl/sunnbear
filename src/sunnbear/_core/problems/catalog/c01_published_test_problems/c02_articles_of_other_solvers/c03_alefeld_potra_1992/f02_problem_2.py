"""This module holds a formula of Alefeld, Potra (1992).

The formula comes from the row with the key ``2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class AlefeldPotra1992Problem2(Formula):
    """This formula comes from Alefeld, Potra (1992).

    The survey writes the source's function as ``x^2*(x^2/3 + sqrt(2)*sin(x)) - sqrt(3)/18``; the formula's interval is
    ``[0.1, 1]``.
    """

    number = (1, 2, 3, 2)
    name = "Problem 2"
    params = ()
    location_in_publication = "Table 1, problem 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\tmp{u}^{2} \left(\frac{\tmp{u}^{2}}{3} + \sqrt{2} \sin{\left(\tmp{u} \right)}\right) - "
            r"\frac{\sqrt{3}}{18}"
        ),
        interval="[0.1, 1]",
        summary=(
            r"A function with 1 simple root, 0.4 above a stationary inflection at $\x = \c$, around which the "
            r"function is nearly flat."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 * (x**2 / 3 + math.sqrt(2) * math.sin(x)) - math.sqrt(3) / 18

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.37, c=0.0, expected=-0.01996698326641826),
        FormulaTestCase.value(params={}, x=0.37, c=0.225, expected=-0.09178137984886615),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 1.0)),
    )
