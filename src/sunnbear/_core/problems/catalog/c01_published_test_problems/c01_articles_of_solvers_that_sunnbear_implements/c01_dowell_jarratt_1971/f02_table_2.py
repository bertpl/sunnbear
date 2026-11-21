"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class DowellJarratt1971Table2(Formula):
    """This formula comes from Dowell, Jarratt (1971).

    The survey writes the source's function as ``2*x*exp(-n) + 1 - 2*exp(-n*x)``, with the parameters ``n = 1, 5, 15,
    20``; the formula's interval is ``[0, 1]``.

    The caption says the function has no turning points or inflection points on `[0, 1]`.
    """

    number = (1, 1, 1, 2)
    name = "Table 2"
    params = (FormulaParam("n", latex_symbol="n"),)
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 2",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"2 \tmp{u} e^{- \param{n}} + 1 - 2 e^{- \param{n} \tmp{u}}",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 2 * x * math.exp(-n) + 1 - 2 * math.exp(-n * x)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",), rows=((1.0,), (5.0,), (15.0,), (20.0,)), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=-0.2609087766605704),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.8656709048842838),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=0.5577824479025916),
        FormulaTestCase.value(params={"n": 15.0}, x=0.3, c=0.0, expected=0.9777821904649077),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=0.9950424968833594),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
