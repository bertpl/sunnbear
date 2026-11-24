"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``29`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem29(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``exp(-x) - cos(3*x) - 0.5``; the formula's interval is ``[0, 1]``.
    """

    number = (1, 2, 18, 13)
    name = "Problem 29"
    params = ()
    location_in_publication = "dataset.json, problem 29"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{- \tmp{u}} - \cos{\left(3 \tmp{u} \right)} - 0.5",
        interval="[0, 1]",
        summary=(
            "A function with 1 root between a shallow minimum 0.38 below that root and a maximum 0.52 above that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(-x) - math.cos(3 * x) - 0.5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.3807917475889466),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.5375416534353282),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
