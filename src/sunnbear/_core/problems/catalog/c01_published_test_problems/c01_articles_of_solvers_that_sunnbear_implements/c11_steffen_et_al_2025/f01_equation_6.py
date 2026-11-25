"""This module holds a formula of Steffen et al. (2025).

The formula comes from the row with the key ``(6)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class SteffenEtAl2025Equation6(Formula):
    """This formula comes from Steffen et al. (2025).

    The survey writes the source's function as ``exp(-x^2/4) - 2*cos(x) + x/2 - 5/2``; the formula's interval is ``[1.0,
    3.0]``.

    3 printed roots: `xi_1 ≈ 2.1584`, `xi_2 ≈ 4.6196`, `xi_3 ≈ 7.2550`; the interval holds `xi_1`.
    """

    number = (1, 1, 11, 1)
    name = "Equation (6)"
    params = ()
    location_in_publication = "Eq. (6)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"e^{- \frac{\tmp{u}^{2}}{4}} - 2 \cos{\left(\tmp{u} \right)} + \frac{\tmp{u}}{2} - " r"\frac{5}{2}"
        ),
        interval="[1, 3]",
        summary="A function with 3 roots, of which only the lowest lies on the interval, 1.2 below a local maximum.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(-(x**2) / 4) - 2 * math.cos(x) + x / 2 - 5 / 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.6, c=0.0, expected=-1.114308531354374),
        FormulaTestCase.value(params={}, x=1.6, c=0.5, expected=-2.1182237545922105),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
    )
