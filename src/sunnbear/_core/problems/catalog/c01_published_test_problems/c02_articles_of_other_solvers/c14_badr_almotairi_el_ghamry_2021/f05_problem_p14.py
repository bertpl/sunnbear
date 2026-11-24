"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P14`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BadrAlmotairiElGhamry2021ProblemP14(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``exp(x) - 3*x - 2``; the formula's interval is ``[2, 3]``.
    """

    number = (1, 2, 14, 5)
    name = "Problem P14"
    params = ()
    location_in_publication = "Table 1, P14"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{\tmp{u}} - 3 \tmp{u} - 2",
        interval="[2, 3]",
        summary="A convex function with 1 simple root on the interval, 1.03 above the function's minimum.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(x) - 3 * x - 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=1.0741824548147194),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=-0.382098893693229),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
