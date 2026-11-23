"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f34`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF34(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``cos(x) - x``; the formula's interval is ``[-11, 9]``.
    """

    number = (1, 1, 13, 6)
    name = "Function f34"
    params = ()
    location_in_publication = "Table 2, f34"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} - \tmp{u}",
        interval="[-11, 9]",
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
        return (-11.0, 9.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-5.0, c=0.0, expected=5.283662185463227),
        FormulaTestCase.value(params={}, x=-5.0, c=0.25, expected=9.160928470923547),
        FormulaTestCase.interval_bounds(params={}, expected=(-11.0, 9.0)),
    )
