"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.8`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction8(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``ceil(10*x - 1) + 1/2``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 19)
    name = "Ill-behaved function 8"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\left\lceil{10 \tmp{u} - 1}\right\rceil + \frac{1}{2}",
        interval="[-1, 1]",
        summary=(
            r"A staircase with unit steps 0.1 apart, taking only half-integer values, so that its sign change at $\x = "
            r"2 \c$ is a jump, not a root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.ceil(10 * x - 1) + 1 / 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-4.5),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-9.5),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
