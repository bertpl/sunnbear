"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``14`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran202514(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``exp(-x) - x - sin(x)``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 3, 3, 2)
    name = "14"
    params = ()
    location_in_publication = "root_tests.f90, case 14"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"e^{- \tmp{u}} - \tmp{u} - \sin{\left(\tmp{u} \right)}",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.exp(-x) - x - math.sin(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.6158308373010088),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=0.7050040013891314),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
