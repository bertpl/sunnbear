"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``70`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case70(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x^2 - 1.0038273894 + sin(x/10000.0)``; the formula's interval is
    ``[0.0001, 10.0001]``.

    the case's `bounds` string says [0.1001, 10.0001]
    """

    number = (1, 3, 3, 22)
    name = "Case 70"
    params = ()
    location_in_publication = "root_tests.f90, case 70"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u}^{2} - 1.0038273894 + \sin{\left(\frac{\tmp{u}}{10000} \right)}",
        interval="[0.0001, 10.0001]",
        summary=(
            r"A parabola plus a nearly linear sine term of at most about $10^{-3}$, flat at $\x = 10 \c$, with 1 root "
            r"on the interval, 1 above that point."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return x**2 - 1.0038273894 + math.sin(x / 10000.0)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0001, 10.0001)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.0001, c=0.0, expected=7.9970726305955),
        FormulaTestCase.value(params={}, x=3.0001, c=0.25, expected=-0.7536773694000206),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0001, 10.0001)),
    )
