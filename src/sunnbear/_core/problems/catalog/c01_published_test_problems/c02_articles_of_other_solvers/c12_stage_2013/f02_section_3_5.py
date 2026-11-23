"""This module holds a formula of Stage (2013).

The formula comes from the row with the key ``3.5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Stage2013Section35(Formula):
    """This formula comes from Stage (2013).

    The survey writes the source's function as ``cos(x) - x``; the formula's interval is ``[-10, 10]``.
    """

    number = (1, 2, 12, 2)
    name = "Section 3.5"
    params = ()
    location_in_publication = "§3.5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} - \tmp{u}",
        interval="[-10, 10]",
        summary=(
            "A decreasing function whose root is the fixed point of the cosine, with 3 inflections where its slope is "
            "0."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return math.cos(x) - x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=3.346356379136388),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=8.088869738115323),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
