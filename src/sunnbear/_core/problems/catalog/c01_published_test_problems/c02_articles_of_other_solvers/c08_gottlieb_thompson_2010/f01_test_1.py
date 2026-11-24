"""This module holds a formula of Gottlieb, Thompson (2010).

The formula comes from the row with the key ``1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GottliebThompson2010Test1(Formula):
    """This formula comes from Gottlieb, Thompson (2010).

    The survey writes the source's function as ``3*sin(x) - 2``; the formula's interval is ``[0, 1]``.

    Table 2's root `0.7297276562`.
    """

    number = (1, 2, 8, 1)
    name = "Test 1"
    params = ()
    location_in_publication = "Table 1, test 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"3 \sin{\left(\tmp{u} \right)} - 2",
        interval="[0, 1]",
        summary="A sine with 1 simple root 0.84 below a maximum at which the function reaches only 1.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 3 * math.sin(x) - 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-1.1134393800159814),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-1.8500624921879651),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
