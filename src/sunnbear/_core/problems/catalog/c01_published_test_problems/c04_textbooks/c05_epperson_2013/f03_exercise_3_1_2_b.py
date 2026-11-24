"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-2(b)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Exercise312B(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``log(x) + x``; the formula's interval is ``[1/10, 1]``.

    3.1-2 asks for the root to an accuracy of 0.1 by bisection, by hand.
    """

    number = (1, 4, 5, 3)
    name = "Exercise 3.1-2(b)"
    params = ()
    location_in_publication = "Exercise 3.1-2(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.9 \c"),),
        expression=r"\ln{\left(\tmp{u} \right)} + \tmp{u}",
        interval="[0.1, 1]",
        summary=(
            r"An increasing function, steepest at the lower bound, with 1 root, at $\x = \Omega + 0.9 \c$, the omega "
            r"constant shifted by $0.9 \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.9 * c
        return math.log(x) + x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.37, c=0.0, expected=-0.6242522733438669),
        FormulaTestCase.value(params={}, x=0.37, c=0.25, expected=-1.7860215365615628),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 1.0)),
    )
