"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction3(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``(x - 1/3)^2*atan(x - 1/3)``; the formula's interval is ``[-1, 1]``.

    The article writes `atan` as `tan^-1`.
    """

    number = (1, 1, 9, 14)
    name = "Ill-behaved function 3"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\left(\tmp{u} - \frac{1}{3}\right)^{2} \arctan{\left(\tmp{u} - \frac{1}{3} \right)}",
        interval="[-1, 1]",
        summary=(
            "A square times an arctangent, forming a triple root, with the function below $10^{-3}$ in magnitude "
            "within 0.1 of that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x - 1 / 3) ** 2 * math.atan(x - 1 / 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.34027826237895187),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-1.3530254455146091),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
