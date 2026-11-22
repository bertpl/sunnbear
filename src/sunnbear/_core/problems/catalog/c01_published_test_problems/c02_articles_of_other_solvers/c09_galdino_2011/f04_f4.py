"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import sign


class Galdino2011F4(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``(81 - p*(108 - p*(54 - p*(12 - p))))*sign(p - 3)``, where ``p = x +
    1.11111``; the formula's interval is ``[1, 2]``.
    """

    number = (1, 2, 9, 4)
    name = "f4"
    params = ()
    location_in_publication = "Table IV, f4"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - \c"),
            (r"\tmp{p}", r"\tmp{u} + 1.11111"),
        ),
        expression=r"(81 - \tmp{p}(108 - \tmp{p}(54 - \tmp{p}(12 - \tmp{p})))) \operatorname{sgn}(\tmp{p} - 3)",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        p = x + 1.11111
        return (81 - p * (108 - p * (54 - p * (12 - p)))) * sign(p - 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=-0.12026429737796887),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-0.4952449658648378),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
