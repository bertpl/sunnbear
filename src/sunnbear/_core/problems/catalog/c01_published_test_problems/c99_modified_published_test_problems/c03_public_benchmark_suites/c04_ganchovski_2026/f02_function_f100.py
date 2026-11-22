"""This module holds formula f1.99.3.4.2, the modified version of the published formula f1.3.4.2.

A change of formula f1.3.4.2 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import real_root


class ModifiedGanchovski2026FunctionF100(Formula):
    """This formula is the modified version of formula f1.3.4.2, from Ganchovski (2026).

    The survey writes the source's function as ``cbrt((4*x - 3)/x)``; the published interval is ``[0, e]``.

    The root line, `$Root{f_100(x); x ∈ [0; e]}`, is the only `$Root` line in the PDF without `= 0`.

    The formula's interval starts at ``0.03``, right of 0 by 1% of the published interval's width, rounded half up to 1
    significant digit; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` divides by
    0.
    """

    number = (1, 99, 3, 4, 2)
    name = "Function f100"
    params = ()
    location_in_publication = "f100"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.69 \c"),),
        expression=r"\sqrt[3]{\frac{4 \tmp{u} - 3}{\tmp{u}}}",
        interval="[0.03, e]",
        notes=("The interval starts at 0.03, not at the published 0, where the function divides by 0.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.69 * c
        return real_root((4 * x - 3) / x, 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.03, 2.718281828459045)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.836485, c=0.25, expected=-2.4269166802380413),
        FormulaTestCase.interval_bounds(params={}, expected=(0.03, 2.718281828459045)),
    )
