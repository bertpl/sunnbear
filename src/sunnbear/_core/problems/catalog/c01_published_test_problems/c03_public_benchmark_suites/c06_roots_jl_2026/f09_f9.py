"""This module holds a formula of Roots.jl (2026).

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


class RootsJl2026F9(Formula):
    """This formula comes from Roots.jl (2026).

    The survey writes the source's function as ``log(x) + sqrt(x) - 5``; the formula's interval is ``[7.0, 10.0]``.

    The source's starting point is `x0 = 7`.
    """

    number = (1, 3, 6, 9)
    name = "f9"
    params = ()
    location_in_publication = "runbenchmarks.jl, f9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\ln{\left(\tmp{u} \right)} + \sqrt{\tmp{u}} - 5",
        interval="[7, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return math.log(x) + math.sqrt(x) - 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (7.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=7.9, c=0.0, expected=-0.12244337601598487),
        FormulaTestCase.value(params={}, x=7.9, c=0.25, expected=-0.35893925186989606),
        FormulaTestCase.interval_bounds(params={}, expected=(7.0, 10.0)),
    )
