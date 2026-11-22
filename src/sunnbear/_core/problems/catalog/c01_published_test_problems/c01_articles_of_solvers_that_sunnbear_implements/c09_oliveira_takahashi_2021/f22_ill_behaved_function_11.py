"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.11`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction11(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``202*x - 2*floor((2*x + 10^-2)/(2*10^-2)) - 1/10``; the formula's
    interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 22)
    name = "Ill-behaved function 11"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"202 \tmp{u} - 2 \left\lfloor{\frac{2 \tmp{u} + \frac{1}{10^{2}}}{2 "
            r"\frac{1}{10^{2}}}}\right\rfloor - \frac{1}{10}"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return 202 * x - 2 * math.floor((2 * x + 10**-2) / (2 * 10**-2)) - 1 / 10

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.9000000000000045),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-1.9000000000000046),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
