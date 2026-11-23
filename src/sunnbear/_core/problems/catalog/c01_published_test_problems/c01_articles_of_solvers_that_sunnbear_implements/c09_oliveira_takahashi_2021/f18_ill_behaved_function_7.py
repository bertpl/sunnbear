"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.7`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction7(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``(x/2)^2 + ceil(x/2) - 1/2``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 18)
    name = "Ill-behaved function 7"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\left(\frac{\tmp{u}}{2}\right)^{2} + \left\lceil{\frac{\tmp{u}}{2}}\right\rceil - " r"\frac{1}{2}"
        ),
        interval="[-1, 1]",
        summary=(
            r"A parabola plus a unit step, with no root: its only sign change is a jump from $-1/2$ to $1/2$ at $\x = "
            r"0$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x / 2) ** 2 + math.ceil(x / 2) - 1 / 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.46),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.2975),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
