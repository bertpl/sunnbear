"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f26`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF26(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(sin(x) - x/4)^3``; the formula's interval is ``[2, 4]``.
    """

    number = (1, 1, 13, 3)
    name = "Function f26"
    params = ()
    location_in_publication = "Table 2, f26"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\left(\sin{\left(\tmp{u} \right)} - \frac{\tmp{u}}{4}\right)^{3}",
        interval="[2, 4]",
        summary="A function with a triple root, below $10^{-3}$ in magnitude within 0.09 of that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (math.sin(x) - x / 4) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.6, c=0.0, expected=-0.0024330641759796167),
        FormulaTestCase.value(params={}, x=2.6, c=0.5, expected=0.03868627310755442),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 4.0)),
    )
