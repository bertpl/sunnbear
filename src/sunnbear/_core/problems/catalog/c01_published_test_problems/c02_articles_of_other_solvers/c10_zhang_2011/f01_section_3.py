"""This module holds a formula of Zhang (2011).

The formula comes from the row with the key ``3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Zhang2011Section3(Formula):
    """This formula comes from Zhang (2011).

    The survey writes the source's function as ``cos(x) - x^3``; the formula's interval is ``[-4, 4]``.

    Table 1's last interval of the new method is `[0.865470, 0.865474]`.
    """

    number = (1, 2, 10, 1)
    name = "Section 3"
    params = ()
    location_in_publication = "Section 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 8 \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} - \tmp{u}^{3}",
        interval="[-4, 4]",
        summary=r"A function with 1 simple root, decreasing except where it rises by only 0.018 just below $\x = 0$.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 8.0 * c
        return math.cos(x) - x**3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-4.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.6, c=0.0, expected=4.0668004776987114),
        FormulaTestCase.value(params={}, x=-1.6, c=0.25, expected=45.759241583665855),
        FormulaTestCase.interval_bounds(params={}, expected=(-4.0, 4.0)),
    )
