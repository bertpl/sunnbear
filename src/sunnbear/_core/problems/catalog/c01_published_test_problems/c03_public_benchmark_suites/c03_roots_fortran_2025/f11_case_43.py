"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``43`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case43(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``3.0*x*sin(x*20.0)*cos(x) + x - 2.0``; the formula's interval is ``[0,
    0.7]``.
    """

    number = (1, 3, 3, 11)
    name = "Case 43"
    params = ()
    location_in_publication = "root_tests.f90, case 43"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.7 \c"),),
        expression=(
            r"3.0 \tmp{u} \sin{\left(\tmp{u} \cdot 20.0 \right)} \cos{\left(\tmp{u} \right)} + \tmp{u} -" r" 2.0"
        ),
        interval="[0, 0.7]",
        summary=(
            "An oscillation of growing amplitude around a rising line, with only negative local extrema below its 1 "
            "root, which lies close to the upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.7 * c
        return 3.0 * x * math.sin(x * 20.0) * math.cos(x) + x - 2.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.7)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.21, c=0.0, expected=-2.3270296714653926),
        FormulaTestCase.value(params={}, x=0.21, c=0.25, expected=-1.8973985698607856),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 0.7)),
    )
