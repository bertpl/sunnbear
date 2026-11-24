"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem55(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``sin(x) = x^2``; the formula's interval is ``[0.5, 1]``.

    The first nontrivial root, graphically and by bisection to `es = 2%`.
    """

    number = (1, 4, 6, 14)
    name = "Problem 5.5"
    params = ()
    location_in_publication = "Prob. 5.5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.5 \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - \tmp{u}^{2}",
        interval="[0.5, 1]",
        summary="A concave function with 2 roots, a maximum between them, and only the upper root on the interval.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.5 * c
        return (math.sin(x)) - (x**2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.65, c=0.0, expected=0.18268640573603956),
        FormulaTestCase.value(params={}, x=0.65, c=0.25, expected=0.22558800467379783),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.0)),
    )
