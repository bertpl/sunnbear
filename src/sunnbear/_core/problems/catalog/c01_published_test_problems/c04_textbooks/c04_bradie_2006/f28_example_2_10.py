"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``Ex. 2.10; 2.5-11(a); 2.6-4, 2.6-12, 2.6-13`` in the survey of published
test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006Example210(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x*(1 - cos(x))``; the formula's interval is `[-2, 1]` (Ex. 2.10).

    Root 0 of multiplicity 3. Newton from `p0 = 1` converges linearly, at rate 2/3, and bisection on `[-2, 1]` beats it
    (Ex. 2.10); secant from `p0 = -1, p1 = 2` (2.5-11); Aitken on the Newton sequence (2.6-4); both techniques for
    restoring quadratic convergence, from `p0 = 1` (2.6-12). 2.6-13 estimates the multiplicity 3 from the 2.6-4
    sequence.
    """

    number = (1, 4, 4, 28)
    name = "Example 2.10"
    params = ()
    location_in_publication = "Example 2.10; Exercises 2.5-11(a), 2.6-4, 2.6-12, 2.6-13"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\tmp{u} \left(1 - \cos{\left(\tmp{u} \right)}\right)",
        interval="[-2, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x * (1 - math.cos(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.1, c=0.0, expected=-0.601044266431865),
        FormulaTestCase.value(params={}, x=-1.1, c=0.25, expected=-2.359841956625349),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 1.0)),
    )
