"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.2-14(a); 2.5-12(a)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise2214A(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``2 + sin(x) - x``; the formula's interval is ``[2, 3]``.

    Fixed-point iteration to `1E-5` with a function `g` of the reader's choice (2.2-14); Steffensen's method on that `g`
    (2.5-12).
    """

    number = (1, 4, 7, 28)
    name = "Exercise 2.2-14(a)"
    params = ()
    location_in_publication = "Exercises 2.2-14(a), 2.5-12(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"2 + \sin{\left(\tmp{u} \right)} - \tmp{u}",
        interval="[2, 3]",
        summary=(
            r"A decreasing function whose 1 simple root solves the fixed-point equation $\tmp{u} = 2 + \sin(\tmp{u})$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 2 + math.sin(x) - x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=0.4457052121767205),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=0.8373623686333757),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
