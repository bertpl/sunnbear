"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f89`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF89(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``sin(20*x) + 0.1*x - 0.1``; the formula's interval is ``[-4.0, 5.0]``.
    """

    number = (1, 1, 13, 27)
    name = "Function f89"
    params = ()
    location_in_publication = "Table 2, f89"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 9 \c"),),
        expression=r"\sin{\left(20 \tmp{u} \right)} + 0.1 \tmp{u} - 0.1",
        interval="[-4, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 9.0 * c
        return math.sin(20 * x) + 0.1 * x - 0.1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-4.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.3, c=0.0, expected=-0.9925584504796033),
        FormulaTestCase.value(params={}, x=-1.3, c=0.25, expected=-1.4060546532543756),
        FormulaTestCase.interval_bounds(params={}, expected=(-4.0, 5.0)),
    )
