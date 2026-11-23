"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``152`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case152(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``pi - 1.0/x``; the formula's interval is ``[0.05, 5]``.
    """

    number = (1, 3, 3, 42)
    name = "Case 152"
    params = ()
    location_in_publication = "root_tests.f90, case 152"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4.95 \c"),),
        expression=r"\pi - \frac{1.0}{\tmp{u}}",
        interval="[0.05, 5]",
        summary=(
            "An increasing function with a pole just below the lower bound, steep next to that bound and nearly flat "
            "over most of the interval."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.95 * c
        return math.pi - 1.0 / x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.05, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.535, c=0.0, expected=2.4901268555441907),
        FormulaTestCase.value(params={}, x=1.535, c=0.25, expected=-0.2197518842253342),
        FormulaTestCase.interval_bounds(params={}, expected=(0.05, 5.0)),
    )
