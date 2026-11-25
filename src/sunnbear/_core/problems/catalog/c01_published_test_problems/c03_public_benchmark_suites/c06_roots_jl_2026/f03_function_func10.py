"""This module holds a formula of Roots.jl (2026).

The formula comes from the row with the key ``func10`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsJl2026FunctionFunc10(Formula):
    """This formula comes from Roots.jl (2026).

    The survey writes the source's function as ``asin(x^2 - 1) - x/2 + 1``; the formula's interval is `[-0.5, 1.0]`
    (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-0.5` to `0.9`.
    """

    number = (1, 3, 6, 3)
    name = "Function func10"
    params = ()
    location_in_publication = "test_derivative_free.jl, func10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\arcsin{\left(\tmp{u}^{2} - 1 \right)} - \frac{\tmp{u}}{2} + 1",
        interval="[-0.5, 1]",
        summary=(
            "A function with 2 roots and a kink at its minimum, where the argument of the arcsine reaches $-1$, the "
            "edge of the arcsine's domain."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.asin(x**2 - 1) - x / 2 + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.5, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.05, c=0.0, expected=-0.4750709089923888),
        FormulaTestCase.value(params={}, x=-0.05, c=0.375, expected=0.2521800920193261),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.5, 1.0)),
    )
