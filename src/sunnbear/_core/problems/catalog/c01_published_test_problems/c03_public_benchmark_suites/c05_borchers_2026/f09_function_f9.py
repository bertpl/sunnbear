"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f9`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Borchers2026FunctionF9(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``tan(x) - x - 0.0463025``; the formula's interval is ``[-0.9, 1.5]``.

    Printed root: `0.5000000340`
    """

    number = (1, 3, 5, 9)
    name = "Function f9"
    params = ()
    location_in_publication = "§5.6, f9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.4 \c"),),
        expression=r"\tan{\left(\tmp{u} \right)} - \tmp{u} - 0.0463025",
        interval="[-0.9, 1.5]",
        summary=(
            r"A tangent minus a line, with 1 root, nearly constant around $\x = 0$ and steep toward the upper bound, "
            r"which lies close to the tangent's pole at $\pi/2$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.4 * c
        return math.tan(x) - x - 0.0463025

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.9, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.18, c=0.0, expected=-0.048272029040198484),
        FormulaTestCase.value(params={}, x=-0.18, c=0.25, expected=-0.25556403687660495),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.9, 1.5)),
    )
