"""This module holds a formula of Roots.jl (2026).

The formula comes from the row with the key ``f8`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsJl2026FunctionF8(Formula):
    """This formula comes from Roots.jl (2026).

    The survey writes the source's function as ``exp(-x^2 + x + 2) - cos(x) + x^3 + 1``; the formula's interval is
    ``[-2.0, 1.0]``.

    The source's starting point is `x0 = -0.5`.
    """

    number = (1, 3, 6, 8)
    name = "Function f8"
    params = ()
    location_in_publication = "runbenchmarks.jl, f8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"e^{- \tmp{u}^{2} + \tmp{u} + 2} - \cos{\left(\tmp{u} \right)} + \tmp{u}^{3} + 1",
        interval="[-2, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return math.exp(-(x**2) + x + 2) - math.cos(x) + x**3 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.1, c=0.0, expected=-0.05114916520128857),
        FormulaTestCase.value(params={}, x=-1.1, c=0.25, expected=-5.01812322349683),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 1.0)),
    )
