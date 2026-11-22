"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-16(a); 2.2-11(a); 2.3-14; 2.4-14(a); 2.5-18(a)`` in the survey of
published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie20062116A(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``exp(x) + x^2 - x - 4``; the formula's interval is `(1, 2)` (2.3-14).

    All real roots to `1E-6` by bisection, false position, Newton and secant. 2.3-14 compares 3 fixed-point iteration
    functions of the reader's choice for its unique zero on `(1, 2)`. 2.6-8 iterates its fixed-point form `x = log(4 + x
    - x^2)`.
    """

    number = (1, 4, 4, 19)
    name = "2.1-16(a)"
    params = ()
    location_in_publication = "Exercises 2.1-16(a), 2.2-11(a), 2.3-14, 2.4-14(a), 2.5-18(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{\tmp{u}} + \tmp{u}^{2} - \tmp{u} - 4",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(x) + x**2 - x - 4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=0.05929666761924445),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-1.089848881936836),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
