"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f86`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF86(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``exp(x) - 1 - x - x^2/2 - 0.005``; the formula's interval is ``[-2.0,
    2.0]``.
    """

    number = (1, 1, 13, 24)
    name = "Function f86"
    params = ()
    location_in_publication = "Table 2, f86"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"e^{\tmp{u}} - 1 - \tmp{u} - \frac{\tmp{u}^{2}}{2} - 0.005",
        interval="[-2, 2]",
        summary=(
            r"The exponential minus its Taylor polynomial of degree 2, lowered by 0.005, so that its 1 root lies 0.3 "
            r"above a stationary inflection at $\x = 0$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return math.exp(x) - 1 - x - x**2 / 2 - 0.005

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.8, c=0.0, expected=-0.07567103588277842),
        FormulaTestCase.value(params={}, x=-0.8, c=0.25, expected=-0.6597011117784135),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 2.0)),
    )
