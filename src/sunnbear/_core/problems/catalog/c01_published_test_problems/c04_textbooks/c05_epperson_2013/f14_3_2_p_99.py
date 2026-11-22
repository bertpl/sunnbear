"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``§3.2 (p. 99), Fig. 3.3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson201332P99(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``(4/3)*exp(2 - x/2)*(1 + x^-1*log(x))``; the formula's interval is `[0,
    8]` (Fig. 3.3).

    Single root near `x = 0.5`. Newton from `x0` in about `[0.8, 1.2]` gives `x1 < 0`, outside the domain; from `x0 >
    1.2` it grows without bound, where `f -> 0`.
    """

    number = (1, 4, 5, 14)
    name = "§3.2 (p. 99)"
    params = ()
    location_in_publication = "§3.2 (p. 99), Fig. 3.3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 8 \c"),),
        expression=(
            r"\frac{4 e^{2 - \frac{\tmp{u}}{2}} \left(1 + \frac{\ln{\left(\tmp{u} " r"\right)}}{\tmp{u}}\right)}{3}"
        ),
        interval="[0, 8]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 8.0 * c
        return (4 / 3) * math.exp(2 - x / 2) * (1 + x**-1 * math.log(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 8.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.4, c=0.0, expected=4.049827630543694),
        FormulaTestCase.value(params={}, x=2.4, c=0.25, expected=-10.411256389941297),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 8.0)),
    )
