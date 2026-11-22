"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``T2.8`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Sabharwal2019Function8(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x*exp(x) - 7``; the formula's interval is ``[-1, 1]``.

    Printed `xe^x - 7`. No sign change and no root on `[-1, 1]`: the only real root is about `1.5243`.
    """

    number = (1, 2, 13, 9)
    name = "Function 8"
    params = ()
    location_in_publication = "Table 2, function 8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u} e^{\tmp{u}} - 7",
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-7.268128018414256),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-7.365912693766539),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
