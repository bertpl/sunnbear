"""This module holds a formula of Li, Zhou, Lange, Tian (2026).

The formula comes from the row with the key ``7.3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class LiZhouLangeTian2026Section73(Formula):
    """This formula comes from Li, Zhou, Lange, Tian (2026).

    The survey writes the source's function as ``-0.5*x - 2*sin(x) + 1``; the formula's interval is `x` in R; starting
    values `x(0) = 0` and `x(0) = x2* + 10^-6` (eq. (7.7)); `[0, 7]` (Fig. 3(a)).

    The function is eq. (7.6), whose stated roots are `x1* = 0.4090497`, `x2* = 3.535612` and `x3* = 5.308993` (Fig. 3).
    From `x(0) = x2* + 10^-6`, the iteration (7.7) converges to `x3*`; eq. (7.8) runs the iteration on the negated
    function from `x(0) = x1* + 10^-6` and converges to `x2*`.
    """

    number = (1, 2, 20, 5)
    name = "Section 7.3"
    params = ()
    location_in_publication = "Section 7.3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"- 0.5 \tmp{u} - 2 \sin{\left(\tmp{u} \right)} + 1",
        interval="[0, 7]",
        summary="A function with 3 simple roots, the upper 2 on either side of a local maximum 0.71 above 0.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return -0.5 * x - 2 * math.sin(x) + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 7.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.1, c=0.0, expected=-1.7764187332977475),
        FormulaTestCase.value(params={}, x=2.1, c=0.175, expected=0.13920438508909708),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 7.0)),
    )
