"""This module holds a formula of Süli, Mayers (2003).

The formula comes from the row with the key ``Examples 1.1–1.3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class SuliMayers2003Example11(Formula):
    """This formula comes from Süli, Mayers (2003).

    The survey writes the source's function as ``exp(x) - 2*x - 1``; the formula's interval is ``[1, 2]``.

    Fixed-point form `x = log(2*x + 1)`, iterated from `x0 = 1` (eq. (1.8), Table 1.1); `x25` is correct to 6 decimals,
    `xi = 1.256431`. Example 1.1 also names `x = (exp(x) - 1)/2`, which does not map `[1, 2]` into itself.
    """

    number = (1, 4, 2, 2)
    name = "Example 1.1"
    params = ()
    location_in_publication = "Examples 1.1–1.3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{\tmp{u}} - 2 \tmp{u} - 1",
        interval="[1, 2]",
        summary="A convex function, 7.5 times as steep at the upper bound as at the lower bound, with 1 simple root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(x) - 2 * x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=0.0692966676192443),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-0.24234888193683618),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
