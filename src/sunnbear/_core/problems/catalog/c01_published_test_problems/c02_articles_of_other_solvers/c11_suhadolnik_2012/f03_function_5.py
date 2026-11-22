"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Suhadolnik2012Function5(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``2*sin(x) - 1``; the formula's interval is ``[.1, pi/3]``.
    """

    number = (1, 2, 11, 3)
    name = "Function 5"
    params = ()
    location_in_publication = "Table 1, function 5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.947 \c"),),
        expression=r"2 \sin{\left(\tmp{u} \right)} - 1",
        interval=r"\left[0.1, \frac{\pi}{3}\right]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.947 * c
        return 2 * math.sin(x) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 1.0471975511965979)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.384159, c=0.0, expected=-0.2504408669108196),
        FormulaTestCase.value(params={}, x=0.384159, c=0.25, expected=-0.7062485442653509),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 1.0471975511965979)),
    )
