"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f7`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026F7(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``x^2 + sin(x/9) - 1/4``; the formula's interval is ``[-0.5, 1.9]``.

    Printed root: `0.4475417621`
    """

    number = (1, 3, 5, 7)
    name = "f7"
    params = ()
    location_in_publication = "§5.6, f7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.4 \c"),),
        expression=r"\tmp{u}^{2} + \sin{\left(\frac{\tmp{u}}{9} \right)} - \frac{1}{4}",
        interval="[-0.5, 1.9]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.4 * c
        return x**2 + math.sin(x / 9) - 1 / 4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.5, 1.9)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.22, c=0.0, expected=-0.17715798986782788),
        FormulaTestCase.value(params={}, x=0.22, c=0.25, expected=-0.14780967830152084),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.5, 1.9)),
    )
