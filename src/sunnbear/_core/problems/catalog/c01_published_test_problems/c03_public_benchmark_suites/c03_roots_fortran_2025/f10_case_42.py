"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``42`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case42(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``exp(x) - 2.0*x - 1.0``; the formula's interval is ``[-0.001, 1]``.

    the comment says that "x1" is close to the root, and that the bracket was changed from [0, 3]
    """

    number = (1, 3, 3, 10)
    name = "Case 42"
    params = ()
    location_in_publication = "root_tests.f90, case 42"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{\tmp{u}} - 2.0 \tmp{u} - 1.0",
        interval="[-0.001, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(x) - 2.0 * x - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.001, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.2993, c=0.0, expected=-0.24968576295104566),
        FormulaTestCase.value(params={}, x=0.2993, c=0.25, expected=-0.04806453589010772),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.001, 1.0)),
    )
