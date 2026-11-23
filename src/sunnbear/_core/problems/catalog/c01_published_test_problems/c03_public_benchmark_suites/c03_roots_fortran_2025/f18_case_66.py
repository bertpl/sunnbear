"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``66`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsFortran2025Case66(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``sin(x)*exp(x) + log(x^2 + 1.0)``; the formula's interval is ``[-0.9,
    -0.1]``.
    """

    number = (1, 3, 3, 18)
    name = "Case 66"
    params = ()
    location_in_publication = "root_tests.f90, case 66"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.8 \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} e^{\tmp{u}} + \ln{\left(\tmp{u}^{2} + 1.0 \right)}",
        interval="[-0.9, -0.1]",
        summary=(
            "A function with 1 root, after which it falls to a local minimum and rises again toward the upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.8 * c
        return math.sin(x) * math.exp(x) + math.log(x**2 + 1.0)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.9, -0.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.66, c=0.0, expected=0.0446926171494963),
        FormulaTestCase.value(params={}, x=-0.66, c=0.25, expected=0.23296496475756145),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.9, -0.1)),
    )
