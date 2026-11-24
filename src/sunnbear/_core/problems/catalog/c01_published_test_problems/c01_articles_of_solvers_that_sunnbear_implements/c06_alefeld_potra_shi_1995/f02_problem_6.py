"""This module holds a formula of Alefeld, Potra, Shi (1995).

The formula comes from the row with the key ``6`` in the survey of published test problems.
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


class AlefeldPotraShi1995Problem6(Formula):
    """This formula comes from Alefeld, Potra, Shi (1995).

    The survey writes the source's function as ``2*x*exp(-n) - 2*exp(-n*x) + 1``, with the parameters ``n = 1(1)5,
    20(20)100``; the formula's interval is ``[0, 1]``.

    Driver problem 19.
    """

    number = (1, 1, 6, 2)
    name = "Problem 6"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Table I, problem 6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"2 \tmp{u} e^{- \param{n}} - 2 e^{- \param{n} \tmp{u}} + 1",
        interval="[0, 1]",
        summary=(
            r"An increasing function with 1 simple root, which nears $\x = \c$ as $\param{n}$ grows; for $\param{n} "
            r"\geq 20$, the function is nearly 1 from $5/\param{n}$ above that root upward."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 2 * x * math.exp(-n) - 2 * math.exp(-n * x) + 1

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=((1.0,), (2.0,), (3.0,), (4.0,), (5.0,), (20.0,), (40.0,), (60.0,), (80.0,), (100.0,)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=-0.2609087766605704),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.8656709048842838),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=-0.016422102246085278),
        FormulaTestCase.value(params={"n": 3.0}, x=0.3, c=0.0, expected=0.21673292153952012),
        FormulaTestCase.value(params={"n": 4.0}, x=0.3, c=0.0, expected=0.4086009595088363),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=0.5577824479025916),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=0.9950424968833594),
        FormulaTestCase.value(params={"n": 40.0}, x=0.3, c=0.0, expected=0.9999877115752933),
        FormulaTestCase.value(params={"n": 60.0}, x=0.3, c=0.0, expected=0.9999999695400406),
        FormulaTestCase.value(params={"n": 80.0}, x=0.3, c=0.0, expected=0.9999999999244973),
        FormulaTestCase.value(params={"n": 100.0}, x=0.3, c=0.0, expected=0.9999999999998128),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
