"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``47`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem47(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``cos(x) + 1.0 * (1 - cos(x))^2 - 0.05 * x^2``; the formula's interval is
    ``[3.0, 6.0]``.

    The file's note: "Beam Deflection (Non-linear transcendental)".
    """

    number = (1, 2, 18, 27)
    name = "Problem 47"
    params = ()
    location_in_publication = "dataset.json, problem 47"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=(
            r"\cos{\left(\tmp{u} \right)} + 1.0 \left(1 - \cos{\left(\tmp{u} \right)}\right)^{2} - 0.05 " r"\tmp{u}^{2}"
        ),
        interval="[3, 6]",
        summary="A function with 1 root near the middle of the interval and a maximum just above the lower bound.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return math.cos(x) + 1.0 * (1 - math.cos(x)) ** 2 - 0.05 * x**2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 6.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.9, c=0.0, expected=1.4924100144814652),
        FormulaTestCase.value(params={}, x=3.9, c=0.25, expected=2.5037689766630495),
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 6.0)),
    )
