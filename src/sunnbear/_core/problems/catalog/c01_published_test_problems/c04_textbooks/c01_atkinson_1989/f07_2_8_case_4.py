"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``§2.8 case (4); P34(iv)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Atkinson198928Case4(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``(x - 1)*exp(-1/(x - 1)^2)``; the formula's interval is ``[0, 3]``.

    Root 1 of infinite multiplicity: every derivative vanishes there. Brent's algorithm stops at 0.9277553, where the
    computed ``f`` is 0 (Table 2.15).

    At its root ``x = 1``, where the expression divides by 0, the formula takes its limit 0.
    """

    number = (1, 4, 1, 7)
    name = "§2.8 case (4)"
    params = ()
    location_in_publication = "§2.8 case (4); Problem 34(iv)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } \tmp{u} = 1 \\ "
            r"(\tmp{u} - 1) e^{-1/(\tmp{u} - 1)^2} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[0, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        if x == 1.0:
            # at its root x = 1, the expression divides by 0; the formula takes its limit 0
            return 0.0
        else:
            return (x - 1.0) * math.exp(-1.0 / (x - 1.0) ** 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.0, expected=-3.72007597602067e-45),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-0.21297042461623097),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
