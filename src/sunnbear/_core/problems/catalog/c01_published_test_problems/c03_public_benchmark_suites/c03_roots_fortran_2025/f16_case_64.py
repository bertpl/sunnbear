"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``64`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case64(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``sin(x)^2 - x^2 + 1.0``; the formula's interval is ``[-2, -1]``.
    """

    number = (1, 3, 3, 16)
    name = "Case 64"
    params = ()
    location_in_publication = "root_tests.f90, case 64"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sin^{2}{\left(\tmp{u} \right)} - \tmp{u}^{2} + 1",
        interval="[-2, -1]",
        summary="A concave function, increasing over the interval, with 1 root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sin(x) ** 2 - x**2 + 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, -1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.7, c=0.0, expected=-0.9066009037102694),
        FormulaTestCase.value(params={}, x=-1.7, c=0.25, expected=-1.9395338478999298),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, -1.0)),
    )
