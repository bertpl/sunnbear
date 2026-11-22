"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f6`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Galdino2011F6(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``exp((x - 3)^5) - 1``; the formula's interval is ``[2.5, 3.5]``.

    The appendix states a zero of multiplicity 5 at `x = 3`, under the label `f7`.
    """

    number = (1, 2, 9, 6)
    name = "f6"
    params = ()
    location_in_publication = "Table IV, f6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{\left(\tmp{u} - 3\right)^{5}} - 1",
        interval="[2.5, 3.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp((x - 3) ** 5) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.5, 3.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.8, c=0.0, expected=-0.00031994880546089787),
        FormulaTestCase.value(params={}, x=2.8, c=0.25, expected=-0.018283601758623744),
        FormulaTestCase.interval_bounds(params={}, expected=(2.5, 3.5)),
    )
