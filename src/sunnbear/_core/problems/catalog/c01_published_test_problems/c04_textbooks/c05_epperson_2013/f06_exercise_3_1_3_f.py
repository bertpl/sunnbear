"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-3(f); 3.2-5(c); 3.3-3(a)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Exercise313F(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``1 - 2*x*exp(-x/2)``; the formula's interval is ``[0, 2]``.

    Bisection to `1E-6`; Newton from `x0 = 0`.
    """

    number = (1, 4, 5, 6)
    name = "Exercise 3.1-3(f)"
    params = ()
    location_in_publication = "Exercises 3.1-3(f), 3.2-5(c), 3.3-3(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"1 - 2 \tmp{u} e^{- \frac{\tmp{u}}{2}}",
        interval="[0, 2]",
        summary="A decreasing function with 1 simple root and a stationary minimum at the upper bound.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return 1 - 2 * x * math.exp(-x / 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=0.11101813518193858),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=0.8097541150998573),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
