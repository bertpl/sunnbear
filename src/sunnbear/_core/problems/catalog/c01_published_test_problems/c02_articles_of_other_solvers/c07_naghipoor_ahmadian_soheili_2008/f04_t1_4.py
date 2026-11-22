"""This module holds a formula of Naghipoor, Ahmadian, Soheili (2008).

The formula comes from the row with the key ``T1.4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class NaghipoorAhmadianSoheili2008T14(Formula):
    """This formula comes from Naghipoor, Ahmadian, Soheili (2008).

    The survey writes the source's function as ``1/x - sin(x) + 1``; the formula's interval is ``[-1.3, -0.5]``.

    Table 1 prints the final iterate `x_n` as `-0.6294463362`; the root is `-0.6294464841`.
    """

    number = (1, 2, 7, 4)
    name = "T1.4"
    params = ()
    location_in_publication = "Table 1, equation 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.8 \c"),),
        expression=r"\frac{1}{\tmp{u}} - \sin{\left(\tmp{u} \right)} + 1",
        interval="[-1.3, -0.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.8 * c
        return 1 / x - math.sin(x) + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.3, -0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.06, c=0.0, expected=0.928959255929892),
        FormulaTestCase.value(params={}, x=-1.06, c=0.25, expected=1.158439547939722),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.3, -0.5)),
    )
