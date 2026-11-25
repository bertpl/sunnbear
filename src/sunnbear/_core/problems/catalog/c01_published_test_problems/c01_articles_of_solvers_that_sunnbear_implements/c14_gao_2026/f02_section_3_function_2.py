"""This module holds a formula of Gao (2026).

The formula comes from the row with the key ``S3.2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import real_root


class Gao2026Section3Function2(Formula):
    """This formula comes from Gao (2026).

    The survey writes the source's function as ``x^(1/5)/(1 + abs(x)^(1/5))``; the formula's interval is ``[-5, 10]``.

    Printed with 5th-root signs. Results in Table 1.
    """

    number = (1, 1, 14, 2)
    name = "Section 3, function 2"
    params = ()
    location_in_publication = "Section 3, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\frac{\sqrt[5]{\tmp{u}}}{1 + \sqrt[5]{\left|{\tmp{u}}\right|}}",
        interval="[-5, 10]",
        summary="A function with an infinite slope at its root, nearly flat farther than 1 from that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return real_root(x, 5) / (1 + real_root(abs(x), 5))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-5.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.5, c=0.0, expected=-0.4653980386192365),
        FormulaTestCase.value(params={}, x=-0.5, c=0.375, expected=-0.5718452694455244),
        FormulaTestCase.interval_bounds(params={}, expected=(-5.0, 10.0)),
    )
