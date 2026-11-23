"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-6(b)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise236B(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``log(x - 1) + cos(x - 1)``; the formula's interval is ``[1.3, 2]``.

    As 2.3-6(a).
    """

    number = (1, 4, 7, 35)
    name = "Exercise 2.3-6(b)"
    params = ()
    location_in_publication = "Exercise 2.3-6(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.7 \c"),),
        expression=r"\ln{\left(\tmp{u} - 1 \right)} + \cos{\left(\tmp{u} - 1 \right)}",
        interval="[1.3, 2]",
        summary=(
            "An increasing, concave function with 1 simple root close to the lower bound, which lies 0.3 above the "
            r"logarithm's singularity at $\x = 1$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.7 * c
        return math.log(x - 1) + math.cos(x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.3, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.51, c=0.0, expected=0.19939995438198568),
        FormulaTestCase.value(params={}, x=1.51, c=0.25, expected=-0.1492144375244277),
        FormulaTestCase.interval_bounds(params={}, expected=(1.3, 2.0)),
    )
