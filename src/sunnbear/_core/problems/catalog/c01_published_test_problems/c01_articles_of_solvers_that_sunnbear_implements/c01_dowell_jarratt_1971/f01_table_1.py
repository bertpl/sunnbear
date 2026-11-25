"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class DowellJarratt1971Table1(Formula):
    """This formula comes from Dowell, Jarratt (1971).

    The survey writes the source's function as ``sin(x) - 0.5``; the formula's interval is ``[0, 1.5]``.

    Root `pi/6`. Starting values `x0 = 0.0`, `x1 = 1.5`.
    """

    number = (1, 1, 1, 1)
    name = "Table 1"
    params = ()
    location_in_publication = "Table 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - 0.5",
        interval="[0, 1.5]",
        summary=r"A sine with 1 simple root, $\pi/3$ below the sine's maximum at $\x = \pi/2 + \c$.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sin(x) - 0.5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=-0.06503446588876978),
        FormulaTestCase.value(params={}, x=0.45, c=0.375, expected=-0.42507029272725766),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
