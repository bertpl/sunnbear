"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-6(b); 2.3-11(b)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise216B(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``2*x + 3*cos(x) - exp(x)``; the formula's interval is ``[1, 2]``.

    As 2.1-6(a). 2.1-6(b) prints `[0, 1]`, a misprint: the function is concave there, with `f(0) = 2` and `f(1) =
    0.903`, so it has no zero on `[0, 1]`; 2.3-11(b), which repeats the exercise, gives `[1, 2]`, which holds the zero
    about 1.2397.
    """

    number = (1, 4, 7, 16)
    name = "Exercise 2.1-6(b)"
    params = ()
    location_in_publication = "Exercises 2.1-6(b), 2.3-11(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"2 \tmp{u} + 3 \cos{\left(\tmp{u} \right)} - e^{\tmp{u}}",
        interval="[1, 2]",
        summary="A concave function with 1 simple root, decreasing from a maximum 1 below that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 2 * x + 3 * math.cos(x) - math.exp(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-0.2668001817454822),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=0.7350620256120171),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
