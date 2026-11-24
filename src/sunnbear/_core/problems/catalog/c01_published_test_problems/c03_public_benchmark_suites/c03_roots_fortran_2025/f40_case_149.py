"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``149`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case149(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``sin((x - 7.14)^3)``; the formula's interval is ``[7, 8]``.
    """

    number = (1, 3, 3, 40)
    name = "Case 149"
    params = ()
    location_in_publication = "root_tests.f90, case 149"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sin{\left(\left(\tmp{u} - 7.14\right)^{3} \right)}",
        interval="[7, 8]",
        summary=(
            r"A function with a triple root and values below $3 \cdot 10^{-3}$ in magnitude within 0.14 of that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sin((x - 7.14) ** 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (7.0, 8.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=7.3, c=0.0, expected=0.004095988546763471),
        FormulaTestCase.value(params={}, x=7.3, c=0.25, expected=-0.0007289999354299245),
        FormulaTestCase.interval_bounds(params={}, expected=(7.0, 8.0)),
    )
