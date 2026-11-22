"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``f3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class KumarSrivastav2026FunctionF3(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``atan(x) - 0.3``; the formula's interval is ``[0, 1]``.

    Printed as `arctan(x)`. Stated root `tan(0.3)`.
    """

    number = (1, 2, 19, 2)
    name = "Function f3"
    params = ()
    location_in_publication = "Table 3, f3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\arctan{\left(\tmp{u} \right)} - 0.3",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.atan(x) - 0.3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.008543205522132918),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.2500416042780573),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
