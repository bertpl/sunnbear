"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``f5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class KumarSrivastav2026F5(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``log(1 + x) - 0.4``; the formula's interval is ``[0, 1]``.

    Stated root `e^0.4 - 1`, so the log is natural.
    """

    number = (1, 2, 19, 4)
    name = "f5"
    params = ()
    location_in_publication = "Table 3, f5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\ln{\left(1 + \tmp{u} \right)} - 0.4",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.log(1 + x) - 0.4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.13763573553250896),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.35120983583056803),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
