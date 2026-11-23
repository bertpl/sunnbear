"""This module holds a formula of Roots.jl (2026).

The formula comes from the row with the key ``func11`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsJl2026FunctionFunc11(Formula):
    """This formula comes from Roots.jl (2026).

    The survey writes the source's function as ``exp(-x) - cos(x)``; the formula's interval is `[-2, 2]` (`find_zeros`).

    The source's 10 starting points are evenly spaced from `-2.0` to `2.0`.
    """

    number = (1, 3, 6, 4)
    name = "Function func11"
    params = ()
    location_in_publication = "test_derivative_free.jl, func11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"e^{- \tmp{u}} - \cos{\left(\tmp{u} \right)}",
        interval="[-2, 2]",
        summary=(
            "An exponential minus a cosine, with 1 root on either side of a shallow minimum, and much larger values "
            "toward the lower bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return math.exp(-x) - math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.8, c=0.0, expected=1.5288342191453024),
        FormulaTestCase.value(params={}, x=-0.8, c=0.25, expected=6.276849559106034),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 2.0)),
    )
