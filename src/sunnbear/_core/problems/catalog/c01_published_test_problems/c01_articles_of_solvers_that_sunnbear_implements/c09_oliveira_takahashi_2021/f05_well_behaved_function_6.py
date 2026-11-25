"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.6`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021WellBehavedFunction6(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``pi^x - e``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 5)
    name = "Well-behaved function 6"
    params = ()
    location_in_publication = "Table 1, well-behaved function 6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\pi^{\tmp{u}} - e",
        interval="[-1, 1]",
        summary=r"A convex, increasing exponential in base $\pi$ with 1 simple root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.pi**x - math.e

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-2.085666004549712),
        FormulaTestCase.value(params={}, x=-0.4, c=0.5, expected=-2.361366570221918),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
