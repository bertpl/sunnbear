"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import sign


class OliveiraTakahashi2021IllBehavedFunction4(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``sign(3*x + 1)*(1 - sqrt(1 - (3*x + 1)^2/9^2))``; the formula's interval
    is ``[-1, 1]``.
    """

    number = (1, 1, 9, 15)
    name = "Ill-behaved function 4"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\operatorname{sign}{\left(3 \tmp{u} + 1 \right)} \left(1 - \sqrt{1 - \frac{\left(3 \tmp{u}"
            r" + 1\right)^{2}}{9^{2}}}\right)"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return sign(3 * x + 1) * (1 - math.sqrt(1 - (3 * x + 1) ** 2 / 9**2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.00024694407093399845),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.018001533782093432),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
