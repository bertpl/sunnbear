"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``67`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case67(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``exp(x^2 + 7.0*x - 30.0) - 1.0``; the formula's interval is ``[1,
    3.1]``.
    """

    number = (1, 3, 3, 19)
    name = "Case 67"
    params = ()
    location_in_publication = "root_tests.f90, case 67"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.1 \c"),),
        expression=r"e^{\tmp{u}^{2} + 7.0 \tmp{u} - 30.0} - 1.0",
        interval="[1, 3.1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.1 * c
        return math.exp(x**2 + 7.0 * x - 30.0) - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.63, c=0.0, expected=-0.9999998796786793),
        FormulaTestCase.value(params={}, x=2.47, c=0.25, expected=-0.9999966346379238),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.1)),
    )
