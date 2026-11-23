"""This module holds a formula of Roots.jl (2026).

The formula comes from the row with the key ``f4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class RootsJl2026FunctionF4(Formula):
    """This formula comes from Roots.jl (2026).

    The survey writes the source's function as ``cos(x) - x/2``; the formula's interval is ``[0.0, pi/2]``.

    The source's starting point is `x0 = pi/4`.
    """

    number = (1, 3, 6, 6)
    name = "Function f4"
    params = ()
    location_in_publication = "runbenchmarks.jl, f4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.57 \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} - \frac{\tmp{u}}{2}",
        interval=r"\left[0, \frac{\pi}{2}\right]",
        summary="A cosine minus a line, decreasing over the interval, with 1 root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.57 * c
        return math.cos(x) - x / 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5707963267948966)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.471239, c=0.0, expected=0.6553869778987967),
        FormulaTestCase.value(params={}, x=0.471239, c=0.25, expected=0.9575321861874498),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5707963267948966)),
    )
