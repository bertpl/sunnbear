"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.3-11`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie20062311(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x = exp(-x^2)``; the formula's interval is ``[0, 1]``.

    Unique fixed point on the interval; iteration from `p0 = 0` to `5E-7`, compared with the theoretical bound on the
    number of iterations.
    """

    number = (1, 4, 4, 25)
    name = "2.3-11"
    params = ()
    location_in_publication = "Exercise 2.3-11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} - e^{- \tmp{u}^{2}}",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x) - (math.exp(-(x**2)))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.6139311852712283),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.9475031223974602),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
