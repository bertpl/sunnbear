"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Romadani2025Section52(Formula):
    """This formula comes from Romadani (2025).

    The survey writes the source's function as ``sin(x) - cos(2*x)^3``; the formula's interval is `[2.5, 3]` (the
    bracketing methods); the search for the exact roots runs over [0, 3].

    The article prints `cos(2*x)^3` as `cos^3(2x)`. Its stated roots are `2.758392986844`, in the bracket, and
    `0.383199666746`, which the fixed-point, Aitken and Steffensen methods reach. The function does not change sign on
    `[0, 3]`, which holds both roots.
    """

    number = (1, 2, 17, 2)
    name = "Section 5.2"
    params = ()
    location_in_publication = "Section 5.2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.5 \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - \cos^{3}{\left(2 \tmp{u} \right)}",
        interval="[2.5, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.5 * c
        return math.sin(x) - math.cos(2 * x) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.5, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.65, c=0.0, expected=0.3016541750571082),
        FormulaTestCase.value(params={}, x=2.65, c=0.25, expected=0.5419169962034848),
        FormulaTestCase.interval_bounds(params={}, expected=(2.5, 3.0)),
    )
