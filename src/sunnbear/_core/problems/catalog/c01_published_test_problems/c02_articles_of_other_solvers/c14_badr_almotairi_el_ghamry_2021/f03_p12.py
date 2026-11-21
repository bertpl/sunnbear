"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P12`` in the survey of published test problems.
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


class BadrAlmotairiElGhamry2021P12(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``x^2 + exp(x/2) - 5``; the formula's interval is ``[1, 2]``.
    """

    number = (1, 2, 14, 3)
    name = "P12"
    params = ()
    source = FormulaSource(
        reference=(
            "Badr, E., Almotairi, S., El Ghamry, A. (2021). A comparative study among new hybrid root "
            "finding algorithms and traditional methods. Mathematics 9(11), 1306. "
            "https://doi.org/10.3390/math9111306."
        ),
        location="Table 1, P12",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
        expression=r"\tmp{u}^{2} + e^{\frac{\tmp{u}}{2}} - 5",
        interval="[1, 2]",
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
