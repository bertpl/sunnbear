"""This module holds formula f1.99.1.12.2, the modified version of the published formula f1.1.12.2.

A change of formula f1.1.12.2 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedGorgeyEtAl2025Equation2(Formula):
    """This formula is the modified version of formula f1.1.12.2, from Gorgey et al. (2025).

    The survey writes the source's function as ``log(x)``; the published interval is ``[0, 2]``.

    Root `1`. The text below Table 3 gives the interval `[2, 3.5]`, which holds no root of `log(x)`: the article repeats
    the interval of Equation 1 there, so the row's `interval` leaves `[2, 3.5]` out.

    The formula's interval starts at ``0.02``, right of 0 by 1% of the published interval's width, rounded half up to 1
    significant digit; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a) = log(0)`` is
    not finite.
    """

    number = (1, 99, 1, 12, 2)
    name = "Equation 2"
    params = ()
    location_in_publication = "Equation 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\ln{\left(\tmp{u} \right)}",
        interval="[0.02, 2]",
        summary="The natural logarithm, steepest at the lower bound.",
        notes=(r"The interval starts at 0.02, not at the published 0, where $\ln(\tmp{u})$ is not finite.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.log(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.02, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.614, c=0.495, expected=-2.1286317858706076),
        FormulaTestCase.interval_bounds(params={}, expected=(0.02, 2.0)),
    )
