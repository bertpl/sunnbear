"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Gsl2024FunctionFunc4(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``x*exp(-x)``; the formula's interval is ``[-1/3, 2]``.

    Starting point -2; expected failure from starting point 2, described as "max iterations x -> +Inf"; derivative given
    """

    number = (1, 3, 2, 4)
    name = "Function func4"
    params = ()
    location_in_publication = "test_funcs.c, func4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} e^{- \tmp{u}}",
        interval=r"\left[- \frac{1}{3}, 2\right]",
        summary=(
            "A function with 1 root and a maximum that lies 1 above that root, past which the function decreases and "
            "tends to 0 without changing sign."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.exp(-x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.3333333333333333, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.366667, c=0.0, expected=0.2541150403402077),
        FormulaTestCase.value(params={}, x=0.366667, c=0.5825, expected=-0.26782611907005804),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.3333333333333333, 2.0)),
    )
