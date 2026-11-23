"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 6.13`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem613(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``exp(0.5*x) = 5 - 5*x``; the formula's interval is ``[0, 2]``.

    The root, by a method of the reader's choice to `es = 2%`: the interval for a bracketing method, `x(i) = 0.7` for
    Newton or modified secant, `x(i-1) = 0`, `x(i) = 2` for secant. The book states that from positive initial guesses
    every method except fixed-point iteration converges.
    """

    number = (1, 4, 6, 24)
    name = "Problem 6.13"
    params = ()
    location_in_publication = "Prob. 6.13"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"e^{0.5 \tmp{u}} - \left(5 - 5 \tmp{u}\right)",
        interval="[0, 2]",
        summary=(
            "An increasing convex function whose slope changes by only 16% across the interval, with 1 simple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (math.exp(0.5 * x)) - (5 - 5 * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.650141192423997),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-3.448728903623976),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
