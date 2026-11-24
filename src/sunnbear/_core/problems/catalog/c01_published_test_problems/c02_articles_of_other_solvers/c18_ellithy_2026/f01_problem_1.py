"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem1(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x * exp(x) - 7``; the formula's interval is ``[1, 2]``.
    """

    number = (1, 2, 18, 1)
    name = "Problem 1"
    params = ()
    location_in_publication = "dataset.json, problem 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} e^{\tmp{u}} - 7",
        interval="[1, 2]",
        summary=r"A function whose root is $W(7)$, the Lambert W function at 7, shifted by $\c$.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-2.229914332094982),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-3.999466326033678),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
