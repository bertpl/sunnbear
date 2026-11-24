"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f7`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Galdino2011FunctionF7(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``exp((x - 3)^5) - exp(x - 1)``; the formula's interval is ``[4, 5]``.
    """

    number = (1, 2, 9, 7)
    name = "Function f7"
    params = ()
    location_in_publication = "Table IV, f7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{\left(\tmp{u} - 3\right)^{5}} - e^{\tmp{u} - 1}",
        interval="[4, 5]",
        summary=r"A function that rises from its 1 simple root to about $3 \cdot 10^{7}$ only 0.5 above that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp((x - 3) ** 5) - math.exp(x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.3, c=0.0, expected=13.86104479377484),
        FormulaTestCase.value(params={}, x=4.3, c=0.25, expected=-17.532053742823347),
        FormulaTestCase.interval_bounds(params={}, expected=(4.0, 5.0)),
    )
