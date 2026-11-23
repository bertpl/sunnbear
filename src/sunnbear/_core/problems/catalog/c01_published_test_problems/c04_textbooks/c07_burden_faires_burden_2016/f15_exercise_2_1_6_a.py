"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-6(a); 2.3-11(a)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise216A(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``3*x - exp(x)``; the formula's interval is ``[1, 2]``.

    Bisection to `1E-5` (2.1-6); Newton, secant and false position to `1E-5` (2.3-11).
    """

    number = (1, 4, 7, 15)
    name = "Exercise 2.1-6(a)"
    params = ()
    location_in_publication = "Exercises 2.1-6(a), 2.3-11(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"3 \tmp{u} - e^{\tmp{u}}",
        interval="[1, 2]",
        summary=(
            r"A concave function with 1 simple root and a nearly flat maximum at $\x = \ln(3)$, just above the lower "
            r"bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 3 * x - math.exp(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=0.23070333238075574),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=0.2923488819368362),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
