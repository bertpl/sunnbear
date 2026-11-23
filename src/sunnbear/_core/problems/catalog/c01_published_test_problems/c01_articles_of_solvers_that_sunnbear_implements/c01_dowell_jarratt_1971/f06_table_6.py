"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 6`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class DowellJarratt1971Table6(Formula):
    """This formula comes from Dowell, Jarratt (1971).

    The survey writes the source's function as ``exp(-n*x)*(x - 1) + x^n``, with the parameters ``n = 1, 5, 10, 15``;
    the formula's interval is ``[0, 1]``.

    The caption says the curves lie closer to the x-axis as `n` grows.
    """

    number = (1, 1, 1, 6)
    name = "Table 6"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Table 6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"e^{- \param{n} \tmp{u}} \left(\tmp{u} - 1\right) + \tmp{u}^{\param{n}}",
        interval="[0, 1]",
        summary=(
            r"An increasing function with 1 root, flatter around it as $\param{n}$ grows, and below $10^{-3}$ in "
            r"magnitude over a fifth of the interval at $\param{n} = 15$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(-n * x) * (x - 1) + x**n

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",), rows=((1.0,), (5.0,), (10.0,), (15.0,)), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=-0.21857275447720254),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.8536679532756783),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=-0.1537611121039009),
        FormulaTestCase.value(params={"n": 10.0}, x=0.3, c=0.0, expected=-0.03484504295750476),
        FormulaTestCase.value(params={"n": 15.0}, x=0.3, c=0.0, expected=-0.007776283227862616),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
