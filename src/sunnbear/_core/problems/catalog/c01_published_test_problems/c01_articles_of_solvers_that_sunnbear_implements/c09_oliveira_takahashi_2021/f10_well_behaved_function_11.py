"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.11`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021WellBehavedFunction11(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``Phi(x - 1) - sqrt(2)/4``; the formula's interval is ``[-1, 1]``.

    `Phi` is the cumulative distribution function of the standard normal distribution; the article names the function
    "Normal CDF" but does not define `Phi`. The formula writes `Phi` with `erfc`, and sunnbear's test transcription in
    `tests/solvers/paper_problems/oliveira_takahashi.py` with `erf`.
    """

    number = (1, 1, 9, 10)
    name = "Well-behaved function 11"
    params = ()
    location_in_publication = "Table 1, well-behaved function 11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\Phi{\left(\tmp{u} - 1 \right)} - \frac{\sqrt{2}}{4}",
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (0.5 * math.erfc(-(x - 1) / math.sqrt(2))) - math.sqrt(2) / 4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.2727967313595027),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.324836830777272),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
