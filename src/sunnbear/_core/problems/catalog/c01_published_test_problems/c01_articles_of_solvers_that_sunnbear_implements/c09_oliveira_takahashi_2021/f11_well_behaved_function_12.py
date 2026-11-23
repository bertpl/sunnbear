"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.12`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021WellBehavedFunction12(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``phi(x - 1) - sqrt(2)/4``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 11)
    name = "Well-behaved function 12"
    params = ()
    location_in_publication = "Table 1, well-behaved function 12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\phi{\left(\tmp{u} - 1 \right)} - \frac{\sqrt{2}}{4}",
        interval="[-1, 1]",
        summary=(
            "The normal density minus a constant, with 1 simple root, increasing toward its peak at the upper bound, "
            "where its slope is 0."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (math.exp(-((x - 1) ** 2) / 2) / math.sqrt(2 * math.pi)) - math.sqrt(2) / 4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.2038259249575289),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.2879375758185972),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
