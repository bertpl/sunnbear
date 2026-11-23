"""This module holds a formula of Norton (1985).

The formula comes from the row with the key ``2`` in the survey of published test problems.
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


class Norton1985Function2(Formula):
    """This formula comes from Norton (1985).

    The survey writes the source's function as ``2*x*exp(-n) + 1 - 2*exp(-n*x)``, with the parameters ``n = 2, 5, 10,
    20``; the formula's interval is ``[0, 1]``.

    Group I.
    """

    number = (1, 2, 2, 1)
    name = "Function 2"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Section 4, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"2 \tmp{u} e^{- \param{n}} + 1 - 2 e^{- \param{n} \tmp{u}}",
        interval="[0, 1]",
        summary=(
            r"An increasing function whose root nears the lower bound as $\param{n}$ grows, with values near 1 over "
            r"most of the interval at $\param{n} = 20$."
        ),
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
                names=("n",), rows=((2.0,), (5.0,), (10.0,), (20.0,)), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=-0.016422102246085278),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.25, expected=-0.7961413077482579),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=0.5577824479025916),
        FormulaTestCase.value(params={"n": 10.0}, x=0.3, c=0.0, expected=0.9004531032221296),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=0.9950424968833594),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
