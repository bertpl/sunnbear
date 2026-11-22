"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f85`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026F85(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``sin(x) - 0.5*x - 0.3``; the formula's interval is ``[-10.0, 10.0]``.
    """

    number = (1, 1, 13, 23)
    name = "f85"
    params = ()
    location_in_publication = "Table 2, f85"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - 0.5 \tmp{u} - 0.3",
        interval="[-10, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return math.sin(x) - 0.5 * x - 0.3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=2.456802495307928),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=3.7878815147582436),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
