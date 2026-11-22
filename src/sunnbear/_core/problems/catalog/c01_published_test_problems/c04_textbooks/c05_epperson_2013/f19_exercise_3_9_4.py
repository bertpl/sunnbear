"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.9-4, 3.9-5(d); 3.11-1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Exercise394(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x = 1 + exp(-x)``; the formula's interval is ``[1, 2]``.

    Fixed-point iteration from any `x0` in `[1, 2]` to `1E-5` (3.9-4); from `x0 = 0`, with both Aitken algorithms
    (3.11-1).
    """

    number = (1, 4, 5, 19)
    name = "Exercise 3.9-4"
    params = ()
    location_in_publication = "Exercises 3.9-4, 3.9-5(d), 3.11-1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} - \left(1 + e^{- \tmp{u}}\right)",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x) - (1 + math.exp(-x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=0.02746820696598745),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-0.2999377491111553),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
