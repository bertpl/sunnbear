"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f91`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF91(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``x*sin(1/x) - 0.1 - 0.01``; the formula's interval is ``[0.01, 1.0]``.
    """

    number = (1, 1, 13, 29)
    name = "Function f91"
    params = ()
    location_in_publication = "Table 2, f91"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} \sin{\left(\frac{1}{\tmp{u}} \right)} - 0.1 - 0.01",
        interval="[0.01, 1]",
        summary=(
            r"An oscillation that speeds up and shrinks toward $\x = \c$, with 3 roots, the lower 2 only 0.018 "
            r"apart."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.sin(1 / x) - 0.1 - 0.01

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.307, c=0.0, expected=-0.14545178597021027),
        FormulaTestCase.value(params={}, x=0.307, c=0.2475, expected=-0.16299331518211085),
        FormulaTestCase.interval_bounds(params={}, expected=(0.01, 1.0)),
    )
