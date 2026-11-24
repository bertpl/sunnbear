"""This module holds a formula of Gorgey et al. (2025).

The formula comes from the row with the key ``Equation 4`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GorgeyEtAl2025Equation4(Formula):
    """This formula comes from Gorgey et al. (2025).

    The survey writes the source's function as ``exp((x - 3)^5) - 1``; the formula's interval is ``[2, 4]``.

    Root `3`.
    """

    number = (1, 1, 12, 4)
    name = "Equation 4"
    params = ()
    location_in_publication = "Equation 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"e^{\left(\tmp{u} - 3\right)^{5}} - 1",
        interval="[2, 4]",
        summary=(
            "A function exactly 0 in floating point on a band 0.0012 wide around its root of multiplicity 5, and "
            "increasingly steep above that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.exp((x - 3) ** 5) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.6, c=0.0, expected=-0.010187749699777461),
        FormulaTestCase.value(params={}, x=2.6, c=0.25, expected=-0.4459442690988902),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 4.0)),
    )
