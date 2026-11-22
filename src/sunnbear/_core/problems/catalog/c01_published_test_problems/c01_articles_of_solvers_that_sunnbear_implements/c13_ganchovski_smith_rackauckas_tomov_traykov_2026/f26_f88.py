"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f88`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026F88(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``log(x) - x + 2 - 0.05``; the formula's interval is ``[0.1, 3.0]``.
    """

    number = (1, 1, 13, 26)
    name = "f88"
    params = ()
    location_in_publication = "Table 2, f88"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.9 \c"),),
        expression=r"\ln{\left(\tmp{u} \right)} - \tmp{u} + 2 - 0.05",
        interval="[0.1, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.9 * c
        return math.log(x) - x + 2 - 0.05

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.97, c=0.0, expected=0.9495407925152914),
        FormulaTestCase.value(params={}, x=0.97, c=0.25, expected=0.29850293156258995),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 3.0)),
    )
