"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``41`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case41(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``atan(x)``; the formula's interval is ``[-2, 3]``.
    """

    number = (1, 3, 3, 9)
    name = "Case 41"
    params = ()
    location_in_publication = "root_tests.f90, case 41"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"\arctan{\left(\tmp{u} \right)}",
        interval="[-2, 3]",
        summary="The arctangent, steepest at its 1 root and flattening toward both bounds.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return math.atan(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.5, c=0.0, expected=-0.4636476090008061),
        FormulaTestCase.value(params={}, x=-0.5, c=0.25, expected=-1.0516502125483738),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 3.0)),
    )
