"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``46`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran202546(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``sin(x*10.0) + sin(x*2.0) + atan(x/3.0)*x^2 + exp(x) - 1.0``; the
    formula's interval is ``[-10, 5]``.
    """

    number = (1, 3, 3, 14)
    name = "46"
    params = ()
    location_in_publication = "root_tests.f90, case 46"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 15 \c"),),
        expression=(
            r"\sin{\left(\tmp{u} \cdot 10.0 \right)} + \sin{\left(\tmp{u} \cdot 2.0 \right)} + "
            r"\arctan{\left(\frac{\tmp{u}}{3.0} \right)} \tmp{u}^{2} + e^{\tmp{u}} - 1.0"
        ),
        interval="[-10, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 15.0 * c
        return math.sin(x * 10.0) + math.sin(x * 2.0) + math.atan(x / 3.0) * x**2 + math.exp(x) - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-5.5, c=0.0, expected=-31.4075184033739),
        FormulaTestCase.value(params={}, x=-5.5, c=0.25, expected=-107.24013762885033),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 5.0)),
    )
