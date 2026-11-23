"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-1(b)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise241B(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``cos(x + sqrt(2)) + x*(x/2 + sqrt(2))``; the formula's interval is
    ``[-2, -1]``.

    As 2.4-1(a). With `u = x + sqrt(2)` it equals `cos(u) + u^2/2 - 1`: root `-sqrt(2)` of multiplicity 4.
    """

    number = (1, 4, 7, 42)
    name = "Exercise 2.4-1(b)"
    params = ()
    location_in_publication = "Exercise 2.4-1(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\cos{\left(\tmp{u} + \sqrt{2} \right)} + \tmp{u} \left(\frac{\tmp{u}}{2} + \sqrt{2}\right)",
        interval="[-2, -1]",
        summary=(
            r"A function below 0.005 on the whole interval, with a root of multiplicity 4 and a sign that rounding "
            r"decides within $3 \cdot 10^{-4}$ of that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.cos(x + math.sqrt(2)) + x * (x / 2 + math.sqrt(2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, -1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.7, c=0.0, expected=0.0002771870794075107),
        FormulaTestCase.value(params={}, x=-1.7, c=0.25, expected=0.0034009584801659456),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, -1.0)),
    )
