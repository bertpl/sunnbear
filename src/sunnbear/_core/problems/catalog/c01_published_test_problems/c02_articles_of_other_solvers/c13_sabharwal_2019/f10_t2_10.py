"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``T2.10`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Sabharwal2019T210(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x*sin(x) - 1``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 2, 13, 10)
    name = "T2.10"
    params = ()
    location_in_publication = "Table 2, function 10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u} \sin{\left(\tmp{u} \right)} - 1",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x * math.sin(x) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.6612145159629788),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-0.9900166583353172),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
