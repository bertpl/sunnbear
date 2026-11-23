"""This module holds a formula of Chen, Li (2007).

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


class ChenLi2007Example2(Formula):
    """This formula comes from Chen, Li (2007).

    The survey writes the source's function as ``x - exp(sin(x)) + 1``; the formula's interval is ``[1, 4]``.

    `x0 = 4`. Root 1.69681.
    """

    number = (1, 2, 6, 2)
    name = "Example 2"
    params = ()
    location_in_publication = "Example 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\tmp{u} - e^{\sin{\left(\tmp{u} \right)}} + 1",
        interval="[1, 4]",
        summary=(
            "A function within 0.025 of its minimum over the lower 10% of the interval, then increasing through 1 "
            "simple root in the lower quarter."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x - math.exp(math.sin(x)) + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.9, c=0.0, expected=0.3238395631529812),
        FormulaTestCase.value(params={}, x=1.9, c=0.25, expected=-0.34119855052789855),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 4.0)),
    )
