"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-2(d)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise242D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(3*x) - 27*x^6 + 27*x^4*exp(x) - 9*x^2*exp(2*x)``; the formula's
    interval is ``[3, 5]``.

    As 2.4-2(a). It equals `(exp(x) - 3*x^2)^3`, the cube of 2.3-6(e)'s function.
    """

    number = (1, 4, 7, 48)
    name = "Exercise 2.4-2(d)"
    params = ()
    location_in_publication = "Exercise 2.4-2(d)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"e^{3 \tmp{u}} - 27 \tmp{u}^{6} + 27 \tmp{u}^{4} e^{\tmp{u}} - 9 \tmp{u}^{2} e^{2 \tmp{u}}",
        interval="[3, 5]",
        summary=(
            r"The cube of $e^{\x} - 3 \x^2$ written out as 4 terms that cancel to rounding noise within $3 \cdot "
            r"10^{-5}$ of the triple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.exp(3 * x) - 27 * x**6 + 27 * x**4 * math.exp(x) - 9 * x**2 * math.exp(2 * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.4, c=0.0, expected=12765.110088002586),
        FormulaTestCase.value(params={}, x=3.6, c=0.25, expected=-291.7044964422511),
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 5.0)),
    )
