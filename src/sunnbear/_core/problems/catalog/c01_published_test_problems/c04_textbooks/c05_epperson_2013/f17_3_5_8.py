"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.5-8, 3.5-9`` in the survey of published test problems.
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


class Epperson2013358(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``7*x - cos(2*pi*x)``; the formula's interval is ``[0, 1]``.

    Newton from several `x0` in `[0, 1]`.
    """

    number = (1, 4, 5, 17)
    name = "3.5-8"
    params = ()
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="Exercises 3.5-8, 3.5-9",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
        expression=r"7 \tmp{u} - \cos{\left(2 \pi \tmp{u} \right)}",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 7 * x - math.cos(2 * math.pi * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=2.409016994374947),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.6010565162951537),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
