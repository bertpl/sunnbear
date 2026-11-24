"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.9`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction9(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``x + sin(x*10^6)/10 + 1/10^3``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 1, 9, 20)
    name = "Ill-behaved function 9"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u} + \frac{\sin{\left(\tmp{u} \cdot 10^{6} \right)}}{10} + \frac{1}{10^{3}}",
        interval="[-1, 1]",
        summary=(
            r"A line plus a fast sine of amplitude 0.1, with about 64,000 roots on a band 0.2 wide around $\x = 2 \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x + math.sin(x * 10**6) / 10 + 1 / 10**3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.38474614649849187, atol=2e-10),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.9306282026349928, atol=4e-10),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
