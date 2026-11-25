"""This module holds a formula of Gorgey et al. (2025).

The formula comes from the row with the key ``Equation 5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GorgeyEtAl2025Equation5(Formula):
    """This formula comes from Gorgey et al. (2025).

    The survey writes the source's function as ``x*sin(x) - x^2*exp(x) + exp(-x) + cos(x)``; the formula's interval is
    ``[-1, 1]``.

    Root `0.85638`.
    """

    number = (1, 1, 12, 5)
    name = "Equation 5"
    params = ()
    location_in_publication = "Equation 5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\tmp{u} \sin{\left(\tmp{u} \right)} - \tmp{u}^{2} e^{\tmp{u}} + e^{- \tmp{u}} + "
            r"\cos{\left(\tmp{u} \right)}"
        ),
        interval="[-1, 1]",
        summary=(
            "A decreasing function with 1 simple root, increasingly steep above that root and steepest at the upper "
            "bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.sin(x) - x**2 * math.exp(x) + math.exp(-x) + math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=2.4614018212019135),
        FormulaTestCase.value(params={}, x=-0.4, c=0.5, expected=3.456885873702464),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
