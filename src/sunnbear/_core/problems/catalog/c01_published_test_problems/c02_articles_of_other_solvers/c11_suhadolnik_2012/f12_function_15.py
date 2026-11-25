"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``15`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function15(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``x^2 - sin(x)^2 - 1``; the formula's interval is ``[-1, 2]``.
    """

    number = (1, 2, 11, 12)
    name = "Function 15"
    params = ()
    location_in_publication = "Table 1, function 15"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} - \sin^{2}{\left(\tmp{u} \right)} - 1",
        interval="[-1, 2]",
        summary=(
            r"A function with 1 root on the interval, symmetric about a flat minimum at $\x = \c$, where the first 3 "
            r"derivatives are 0."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - math.sin(x) ** 2 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.1, c=0.0, expected=-0.9999667110793792),
        FormulaTestCase.value(params={}, x=-0.1, c=0.75, expected=-0.8419222471477623),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 2.0)),
    )
