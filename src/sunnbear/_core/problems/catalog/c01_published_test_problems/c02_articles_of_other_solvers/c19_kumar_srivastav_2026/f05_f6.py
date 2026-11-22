"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``f6`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class KumarSrivastav2026F6(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``sin(x) - 0.3``; the formula's interval is ``[0, 2]``.

    Stated root `0.304693...`. The article calls it not monotone on its interval and leaves it out of Tables 4 to 7.
    """

    number = (1, 2, 19, 5)
    name = "f6"
    params = ()
    location_in_publication = "Table 3, f6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - 0.3",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.sin(x) - 0.3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=0.2646424733950353),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-0.20016658335317186),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
