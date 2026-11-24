"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``34`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem34(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``4*sin(x) - x + 1``; the formula's interval is ``[-1, 0]``.
    """

    number = (1, 2, 18, 17)
    name = "Problem 34"
    params = ()
    location_in_publication = "dataset.json, problem 34"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"4 \sin{\left(\tmp{u} \right)} - \tmp{u} + 1",
        interval="[-1, 0]",
        summary=(
            r"A function with 1 simple root, at which the slope is 2.8, close to the slope's largest value of 3, "
            r"reached at $\x = \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 4 * math.sin(x) - x + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.7, c=0.0, expected=-0.8768707489507641),
        FormulaTestCase.value(params={}, x=-0.7, c=0.25, expected=-1.303662019157495),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 0.0)),
    )
