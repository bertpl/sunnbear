"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-1(a)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise241A(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^2 - 2*x*exp(-x) + exp(-2*x)``; the formula's interval is ``[0, 1]``.

    Newton to `1E-5`. It equals `(x - exp(-x))^2`, so its root is double.
    """

    number = (1, 4, 7, 41)
    name = "Exercise 2.4-1(a)"
    params = ()
    location_in_publication = "Exercise 2.4-1(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} - 2 \tmp{u} e^{- \tmp{u}} + e^{- 2 \tmp{u}}",
        interval="[0, 1]",
        summary=(
            r"The square of $\x - e^{-\x}$ written out, never negative in exact arithmetic but negative at many floats "
            r"within $8 \cdot 10^{-9}$ of the double root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - 2 * x * math.exp(-x) + math.exp(-2 * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.19432070368499574),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=0.8122144755858882),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
