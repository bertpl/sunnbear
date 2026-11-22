"""This module holds a formula of Gao (2026).

The formula comes from the row with the key ``S3.1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import real_root


class Gao2026Section3Function1(Formula):
    """This formula comes from Gao (2026).

    The survey writes the source's function as ``x^(1/3)``; the formula's interval is ``[-5, 1]``.

    Steep slope near the root; results in Table 1.
    """

    number = (1, 1, 14, 1)
    name = "Section 3, function 1"
    params = ()
    location_in_publication = "Section 3, function 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 6 \c"),),
        expression=r"\sqrt[3]{\tmp{u}}",
        interval="[-5, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 6.0 * c
        return real_root(x, 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-5.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-3.2, c=0.0, expected=-1.4736125994561546),
        FormulaTestCase.value(params={}, x=-3.2, c=0.25, expected=-1.6750686836022342),
        FormulaTestCase.interval_bounds(params={}, expected=(-5.0, 1.0)),
    )
