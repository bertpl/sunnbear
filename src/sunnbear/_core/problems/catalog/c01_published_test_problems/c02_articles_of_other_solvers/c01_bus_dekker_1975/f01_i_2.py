"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``I.2`` in the survey of published test problems.
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


class BusDekker1975I2(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``2*x*exp(-n) + 1 - 2*exp(-n*x)``, with the parameters ``n = 1, 2, 3,
    4``; the formula's interval is ``[0, 1]``.
    """

    number = (1, 2, 1, 1)
    name = "I.2"
    params = (FormulaParam("n", latex_symbol="n"),)
    source = FormulaSource(
        reference=(
            "Bus, J. C. P., Dekker, T. J. (1975). Two efficient algorithms with guaranteed convergence "
            "for finding a zero of a function. ACM Transactions on Mathematical Software 1(4), 330–345."
            " https://doi.org/10.1145/355656.355659."
        ),
        location="Group I, function 2",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
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
            ParamTable(names=("n",), rows=((1.0,), (2.0,), (3.0,), (4.0,)), summary="The published parameter values."),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=-0.2609087766605704),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.8656709048842838),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=-0.016422102246085278),
        FormulaTestCase.value(params={"n": 3.0}, x=0.3, c=0.0, expected=0.21673292153952012),
        FormulaTestCase.value(params={"n": 4.0}, x=0.3, c=0.0, expected=0.4086009595088363),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
