"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``68`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran202568(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x - 3.0*log(x)``; the formula's interval is ``[1, 2.1]``.
    """

    number = (1, 3, 3, 20)
    name = "68"
    params = ()
    location_in_publication = "root_tests.f90, case 68"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.1 \c"),),
        expression=r"\tmp{u} - 3.0 \ln{\left(\tmp{u} \right)}",
        interval="[1, 2.1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.1 * c
        return x - 3.0 * math.log(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.33, c=0.0, expected=0.4744631732990127),
        FormulaTestCase.value(params={}, x=1.33, c=0.25, expected=0.8943776992159103),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.1)),
    )
