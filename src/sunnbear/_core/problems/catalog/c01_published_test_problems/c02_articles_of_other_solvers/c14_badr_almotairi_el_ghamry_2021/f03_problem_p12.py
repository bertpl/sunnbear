"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P12`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BadrAlmotairiElGhamry2021ProblemP12(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``x^2 + exp(x/2) - 5``; the formula's interval is ``[1, 2]``.
    """

    number = (1, 2, 14, 3)
    name = "Problem P12"
    params = ()
    location_in_publication = "Table 1, P12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} + e^{\frac{\tmp{u}}{2}} - 5",
        interval="[1, 2]",
        summary=(
            "A function whose slope nearly doubles across the interval, with 1 simple root past the interval's middle."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 + math.exp(x / 2) - 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-1.3944591709861038),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-2.2070411516209085),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
