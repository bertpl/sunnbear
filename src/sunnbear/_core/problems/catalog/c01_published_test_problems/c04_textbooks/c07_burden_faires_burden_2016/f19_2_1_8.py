"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-8; 2.2-16`` in the survey of published test problems.
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


class BurdenFairesBurden2016218(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = tan(x)``; the formula's interval is `[4, 5]` (2.2-16).

    The first positive solution by bisection to `1E-5` (2.1-8); the solution in `[4, 5]` by fixed-point iteration to
    `1E-4` (2.2-16).
    """

    number = (1, 4, 7, 19)
    name = "2.1-8"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="Exercises 2.1-8, 2.2-16",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} - \tan{\left(\tmp{u} \right)}",
        interval="[4, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x) - (math.tan(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.3, c=0.0, expected=2.01415212263302),
        FormulaTestCase.value(params={}, x=4.3, c=0.25, expected=2.7678500693266757),
        FormulaTestCase.interval_bounds(params={}, expected=(4.0, 5.0)),
    )
