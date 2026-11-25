"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f46`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF46(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(exp(-5*x) - x - 0.5)/x^5``; the formula's interval is ``[0.09, 0.7]``.
    """

    number = (1, 1, 13, 16)
    name = "Function f46"
    params = ()
    location_in_publication = "Table 2, f46"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\frac{e^{- 5 \tmp{u}} - \tmp{u} - 0.5}{\tmp{u}^{5}}",
        interval="[0.09, 0.7]",
        summary=(
            "A function with a pole of order 5 below the lower bound, 1 simple root 0.1 above that pole, and a deep "
            "minimum just above the root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (math.exp(-5 * x) - x - 0.5) / x**5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.09, 0.7)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.273, c=0.0, expected=-341.3479083845647),
        FormulaTestCase.value(params={}, x=0.273, c=0.1525, expected=-2875.6536869539377),
        FormulaTestCase.interval_bounds(params={}, expected=(0.09, 0.7)),
    )
