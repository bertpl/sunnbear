"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``8`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function8(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``cos(x) - x``; the formula's interval is ``[0, 1.7]``.
    """

    number = (1, 2, 11, 5)
    name = "Function 8"
    params = ()
    location_in_publication = "Table 1, function 8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.7 \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} - \tmp{u}",
        interval="[0, 1.7]",
        summary=r"A decreasing function with 1 root, at $1.7 \c$ plus the fixed point of the cosine.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.7 * c
        return math.cos(x) - x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.7)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.51, c=0.0, expected=0.3627445076457512),
        FormulaTestCase.value(params={}, x=0.51, c=0.25, expected=0.9113896745022905),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.7)),
    )
