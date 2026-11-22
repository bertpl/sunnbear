"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2.4 Ex. 1, 2; Fig. 2.11; Tables 2.8, 2.9`` in the survey of published
test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Section24Example1(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(x) - x - 1``; the formula's interval is `[-1, 1]` (Fig. 2.11).

    Root 0 of multiplicity 2. Newton from `p0 = 1` converges, but not quadratically (Ex. 1, Table 2.8, 16 iterations);
    the modified Newton method (2.13) from `p0 = 1` (Ex. 2, Table 2.9), whose last iterates improve little in 10-digit
    arithmetic.
    """

    number = (1, 4, 7, 8)
    name = "Section 2.4, example 1"
    params = ()
    location_in_publication = "§2.4 Examples 1, 2; Fig. 2.11; Tables 2.8, 2.9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"e^{\tmp{u}} - \tmp{u} - 1",
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.exp(x) - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=0.07032004603563931),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=0.30656965974059913),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
