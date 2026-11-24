"""This module holds a formula of Gorgey et al. (2025).

The formula comes from the row with the key ``Equation 2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GorgeyEtAl2025Equation2(Formula):
    """This formula comes from Gorgey et al. (2025).

    The survey writes the source's function as ``log(x)``; the formula's interval is ``[0, 2]``.

    Root `1`. The text below Table 3 gives the interval `[2, 3.5]`, which holds no root of `log(x)`: the article repeats
    the interval of Equation 1 there, so the row's `interval` leaves `[2, 3.5]` out.
    """

    number = (1, 1, 12, 2)
    name = "Equation 2"
    params = ()
    location_in_publication = "Equation 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\ln{\left(\tmp{u} \right)}",
        interval="[0, 2]",
        summary=r"The natural logarithm, which tends to $-\infty$ at $\x = 2 \c$ and is steep next to that point.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.log(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.5108256237659907),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-2.302585092994046),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
