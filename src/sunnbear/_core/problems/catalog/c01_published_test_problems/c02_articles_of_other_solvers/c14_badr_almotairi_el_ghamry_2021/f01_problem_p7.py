"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P7`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BadrAlmotairiElGhamry2021ProblemP7(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``x*exp(x) - 7``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 2, 14, 1)
    name = "Problem P7"
    params = ()
    location_in_publication = "Table 1, P7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u} e^{\tmp{u}} - 7",
        interval="[0, 2]",
        summary=(
            r"An increasing convex function with 1 simple root, at $\c$ plus the value of the Lambert W function at "
            r"7."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-5.906728719765694),
        FormulaTestCase.value(params={}, x=0.6, c=0.5, expected=-6.889482908192435),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
