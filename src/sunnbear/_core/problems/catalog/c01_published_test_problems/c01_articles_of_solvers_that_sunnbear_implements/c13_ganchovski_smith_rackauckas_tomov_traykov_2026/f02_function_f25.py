"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f25`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF25(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(x - 4)^5*log(x)``; the formula's interval is ``[3.6, 5.6]``.
    """

    number = (1, 1, 13, 2)
    name = "Function f25"
    params = ()
    location_in_publication = "Table 2, f25"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\left(\tmp{u} - 4\right)^{5} \ln{\left(\tmp{u} \right)}",
        interval="[3.6, 5.6]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x - 4) ** 5 * math.log(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.6, 5.6)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.2, c=0.0, expected=0.0004592270480925853),
        FormulaTestCase.value(params={}, x=4.2, c=0.25, expected=-0.0031792487517499253),
        FormulaTestCase.interval_bounds(params={}, expected=(3.6, 5.6)),
    )
