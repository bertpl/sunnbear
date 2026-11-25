"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function2(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``(10 - x)*exp(-10*x) - x^10 + 1``; the formula's interval is ``[.5,
    8]``.
    """

    number = (1, 2, 11, 1)
    name = "Function 2"
    params = ()
    location_in_publication = "Table 1, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\left(10 - \tmp{u}\right) e^{- 10 \tmp{u}} - \tmp{u}^{10} + 1",
        interval="[0.5, 8]",
        summary=r"A decreasing function with 1 root only $4 \cdot 10^{-5}$ above $\x = 1 + 10 \c$.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return (10 - x) * math.exp(-10 * x) - x**10 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 8.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.75, c=0.0, expected=-24734.85567569732),
        FormulaTestCase.value(params={}, x=2.75, c=0.1875, expected=0.7383703834278529),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 8.0)),
    )
