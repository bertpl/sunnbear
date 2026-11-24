"""This module holds a formula of Naghipoor, Ahmadian, Soheili (2008).

The formula comes from the row with the key ``T1.1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class NaghipoorAhmadianSoheili2008Equation1(Formula):
    """This formula comes from Naghipoor, Ahmadian, Soheili (2008).

    The survey writes the source's function as ``x*exp(x) - 1``; the formula's interval is ``[-1, 1]``.

    Table 1 prints the final iterate `x_n` as `0.5671433083`; the root is `0.5671432904`.
    """

    number = (1, 2, 7, 1)
    name = "Equation 1"
    params = ()
    location_in_publication = "Table 1, equation 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u} e^{\tmp{u}} - 1",
        interval="[-1, 1]",
        summary=r"A function with 1 root, at $2 \c$ plus the omega constant, and a minimum 1.57 below that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x * math.exp(x) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-1.2681280184142558),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-1.3659126937665391),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
