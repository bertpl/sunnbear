"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-1`` in the survey of published test problems.
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


class BurdenFairesBurden2016211(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``sqrt(x) - cos(x)``; the formula's interval is ``[0, 1]``.

    Bisection to `p3`.
    """

    number = (1, 4, 7, 9)
    name = "2.1-1"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="Exercise 2.1-1",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sqrt{\tmp{u}} - \cos{\left(\tmp{u} \right)}",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sqrt(x) - math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.4076139316204399),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.7751434626449873),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
