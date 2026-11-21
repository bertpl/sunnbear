"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``7`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik20127(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``(x - 1)*exp(-x)``; the formula's interval is ``[0, 1.5]``.
    """

    number = (1, 2, 11, 4)
    name = "7"
    params = ()
    source = FormulaSource(
        reference=(
            "Suhadolnik, A. (2012). Combined bracketing methods for solving nonlinear equations. "
            "Applied Mathematics Letters 25(11), 1755–1760. https://doi.org/10.1016/j.aml.2012.02.006."
        ),
        location="Table 1, function 7",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\left(\tmp{u} - 1\right) e^{- \tmp{u}}",
        interval="[0, 1.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return (x - 1) * math.exp(-x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=-0.3506954833919753),
        FormulaTestCase.value(params={}, x=0.45, c=0.25, expected=-0.8581627248539114),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
