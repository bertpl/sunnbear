"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Galdino2011FunctionF5(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``sin((x - 7.143)^3)``; the formula's interval is ``[7, 8]``.

    The appendix states a zero of multiplicity 3 at `x = 7.143`.
    """

    number = (1, 2, 9, 5)
    name = "Function f5"
    params = ()
    location_in_publication = "Table IV, f5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\sin{\left(\left(\tmp{u} - 7.143\right)^{3} \right)}",
        interval="[7, 8]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.sin((x - 7.143) ** 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (7.0, 8.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=7.3, c=0.0, expected=0.0038698833407079616),
        FormulaTestCase.value(params={}, x=7.3, c=0.25, expected=-0.0008043569132648269),
        FormulaTestCase.interval_bounds(params={}, expected=(7.0, 8.0)),
    )
