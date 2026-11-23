"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``150`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case150(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``exp((x - 3.0)^5) - 1.0``; the formula's interval is ``[2.6, 3.6]``.
    """

    number = (1, 3, 3, 41)
    name = "Case 150"
    params = ()
    location_in_publication = "root_tests.f90, case 150"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{\left(\tmp{u} - 3.0\right)^{5}} - 1.0",
        interval="[2.6, 3.6]",
        summary=(
            "A function with a root of multiplicity 5, around which it is exactly 0 in floating point on a band "
            "0.0012 wide."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp((x - 3.0) ** 5) - 1.0

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.6, 3.6)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.9, c=0.0, expected=-9.99995000016671e-06),
        FormulaTestCase.value(params={}, x=2.9, c=0.25, expected=-0.005238418878905655),
        FormulaTestCase.interval_bounds(params={}, expected=(2.6, 3.6)),
    )
