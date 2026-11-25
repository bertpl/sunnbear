"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f10`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026FunctionF10(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``x^2 + x*sin(sqrt(75)*x) - 0.2``; the formula's interval is ``[0.4,
    1]``.

    Printed root: `0.6798089215`
    """

    number = (1, 3, 5, 10)
    name = "Function f10"
    params = ()
    location_in_publication = "§5.6, f10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} + \tmp{u} \sin{\left(\sqrt{75} \tmp{u} \right)} - 0.2",
        interval="[0.4, 1]",
        summary=(
            "A function with 1 root between 2 local extrema: a minimum 0.14 below the root and a maximum 0.27 above it."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 + x * math.sin(math.sqrt(75) * x) - 0.2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.4, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.58, c=0.0, expected=-0.4158545912856281),
        FormulaTestCase.value(params={}, x=0.58, c=0.15, expected=-0.2515828857630686),
        FormulaTestCase.interval_bounds(params={}, expected=(0.4, 1.0)),
    )
