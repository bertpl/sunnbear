"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-6(a)`` in the survey of published test problems.
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


class BurdenFairesBurden2016236A(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(x) + 2^-x + 2*cos(x) - 6``; the formula's interval is ``[1, 2]``.

    Newton to `1E-5`.
    """

    number = (1, 4, 7, 34)
    name = "2.3-6(a)"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="Exercise 2.3-6(a)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
        expression=r"e^{\tmp{u}} + 2^{- \tmp{u}} + 2 \cos{\left(\tmp{u} \right)} - 6",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(x) + 2**-x + 2 * math.cos(x) - 6

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-1.389579476953463),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-1.6642386216909595),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
