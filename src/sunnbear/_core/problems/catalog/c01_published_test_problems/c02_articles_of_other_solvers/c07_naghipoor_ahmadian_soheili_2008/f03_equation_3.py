"""This module holds a formula of Naghipoor, Ahmadian, Soheili (2008).

The formula comes from the row with the key ``T1.3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class NaghipoorAhmadianSoheili2008Equation3(Formula):
    """This formula comes from Naghipoor, Ahmadian, Soheili (2008).

    The survey writes the source's function as ``exp(x^2 + 7*x - 30) - 1``; the formula's interval is ``[2.8, 3.1]``.

    Table 1 prints the final iterate `x_n` as `3.0000000000`.
    """

    number = (1, 2, 7, 3)
    name = "Equation 3"
    params = ()
    location_in_publication = "Table 1, equation 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.3 \c"),),
        expression=r"e^{\tmp{u}^{2} + 7 \tmp{u} - 30} - 1",
        interval="[2.8, 3.1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.3 * c
        return math.exp(x**2 + 7 * x - 30) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.8, 3.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.89, c=0.0, expected=-0.7577778503147906),
        FormulaTestCase.value(params={}, x=2.89, c=0.25, expected=-0.9065916932186274),
        FormulaTestCase.interval_bounds(params={}, expected=(2.8, 3.1)),
    )
