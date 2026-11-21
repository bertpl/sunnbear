"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-1(a)`` in the survey of published test problems.
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


class BurdenFairesBurden2016241A(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^2 - 2*x*exp(-x) + exp(-2*x)``; the formula's interval is ``[0, 1]``.

    Newton to `1E-5`. It equals `(x - exp(-x))^2`, so its root is double.
    """

    number = (1, 4, 7, 41)
    name = "2.4-1(a)"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="Exercise 2.4-1(a)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
        expression=r"\tmp{u}^{2} - 2 \tmp{u} e^{- \tmp{u}} + e^{- 2 \tmp{u}}",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - 2 * x * math.exp(-x) + math.exp(-2 * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.19432070368499574),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=0.8122144755858882),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
