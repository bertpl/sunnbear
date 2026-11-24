"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``154`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case154(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``2.0*x*exp(-5.0) - 2.0*exp(-5.0*x) + 1.0``; the formula's interval is
    ``[0, 10]``.
    """

    number = (1, 3, 3, 43)
    name = "Case 154"
    params = ()
    location_in_publication = "root_tests.f90, case 154"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\frac{2.0 \tmp{u}}{e^{5.0}} - 2.0 e^{- 5.0 \tmp{u}} + 1.0",
        interval="[0, 10]",
        summary="An increasing function that rises quickly through its root to about 1 and is then nearly flat.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return 2.0 * x * math.exp(-5.0) - 2.0 * math.exp(-5.0 * x) + 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.0, c=0.0, expected=1.040427070189872),
        FormulaTestCase.value(params={}, x=3.0, c=0.25, expected=0.8425679497512879),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 10.0)),
    )
