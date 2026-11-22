"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f35`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF35(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``sqrt(abs(x - 2/3))*if(x <= 2/3; 1; -1) - 0.1``; the formula's interval
    is ``[-11, 9]``.
    """

    number = (1, 1, 13, 7)
    name = "Function f35"
    params = ()
    location_in_publication = "Table 2, f35"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=(
            r"\sqrt{\left|{\tmp{u} - \frac{2}{3}}\right|} \left(\begin{cases} 1 & \text{for}\: \tmp{u} "
            r"\leq \frac{2}{3} \\-1 & \text{otherwise} \end{cases}\right) - 0.1"
        ),
        interval="[-11, 9]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return math.sqrt(abs(x - 2 / 3)) * ((1) if (x) <= (2 / 3) else (-1)) - 0.1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-11.0, 9.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-5.0, c=0.0, expected=2.2804761428476166),
        FormulaTestCase.value(params={}, x=-5.0, c=0.25, expected=3.165986323710904),
        FormulaTestCase.interval_bounds(params={}, expected=(-11.0, 9.0)),
    )
