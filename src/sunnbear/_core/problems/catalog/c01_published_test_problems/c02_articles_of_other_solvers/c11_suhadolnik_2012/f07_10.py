"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``10`` in the survey of published test problems.
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


class Suhadolnik201210(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``exp(x^2 + 7*x - 30) - 1``; the formula's interval is ``[2.6, 3.5]``.
    """

    number = (1, 2, 11, 7)
    name = "10"
    params = ()
    source = FormulaSource(
        reference=(
            "Suhadolnik, A. (2012). Combined bracketing methods for solving nonlinear equations. "
            "Applied Mathematics Letters 25(11), 1755–1760. https://doi.org/10.1016/j.aml.2012.02.006."
        ),
        location="Table 1, function 10",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.9 \c"),),
        expression=r"e^{\tmp{u}^{2} + 7 \tmp{u} - 30} - 1",
        interval="[2.6, 3.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.9 * c
        return math.exp(x**2 + 7 * x - 30) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.6, 3.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.87, c=0.0, expected=-0.8123355966715369),
        FormulaTestCase.value(params={}, x=2.87, c=0.25, expected=-0.9887678491341472),
        FormulaTestCase.interval_bounds(params={}, expected=(2.6, 3.5)),
    )
