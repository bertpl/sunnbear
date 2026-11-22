"""This module holds a formula of Ganchovski (2026).

The formula comes from the row with the key ``f100`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import real_root


class Ganchovski2026F100(Formula):
    """This formula comes from Ganchovski (2026).

    The survey writes the source's function as ``cbrt((4*x - 3)/x)``; the formula's interval is ``[0, e]``.

    The root line, `$Root{f_100(x); x ∈ [0; e]}`, is the only `$Root` line in the PDF without `= 0`.
    """

    number = (1, 3, 4, 2)
    name = "f100"
    params = ()
    location_in_publication = "f100"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.72 \c"),),
        expression=r"\sqrt[3]{\frac{4 \tmp{u} - 3}{\tmp{u}}}",
        interval="[0, e]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.72 * c
        return real_root((4 * x - 3) / x, 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.718281828459045)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.815485, c=0.0, expected=0.6848497192199624),
        FormulaTestCase.value(params={}, x=0.815485, c=0.25, expected=-2.62764740296579),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.718281828459045)),
    )
