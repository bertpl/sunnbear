"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-10`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise2110(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^2 - 1 = exp(1 - x^2)``; the formula's interval is ``[-2, 0]``.

    Bisection to `1E-3`, after a sketch of both sides.
    """

    number = (1, 4, 7, 21)
    name = "Exercise 2.1-10"
    params = ()
    location_in_publication = "Exercise 2.1-10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u}^{2} - 1 - e^{1 - \tmp{u}^{2}}",
        interval="[-2, 0]",
        summary=(
            "An even function, decreasing on the interval through 1 simple root to the function's minimum at the "
            "upper bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x**2 - 1) - (math.exp(1 - x**2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.4, c=0.0, expected=0.5771071140248877),
        FormulaTestCase.value(params={}, x=-1.4, c=0.25, expected=2.5364654562369426),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 0.0)),
    )
