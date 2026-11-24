"""This module holds a formula of Alefeld, Potra, Shi (1993).

The formula comes from the row with the key ``T5.1-3`` in the survey of published test problems.
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


class AlefeldPotraShi1993Problem3(Formula):
    """This formula comes from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``a*x*exp(b*x)``, with the parameters `a = -40, b = -1`; `a = -100, b =
    -2`; `a = -200, b = -3`; the formula's interval is ``[-9, 31]``.

    """

    number = (1, 2, 4, 3)
    name = "Problem 3"
    params = (
        FormulaParam("w", latex_symbol="w", meaning=r"The factor that multiplies $\tmp{u} e^{\param{k} \tmp{u}}$."),
        FormulaParam("k", latex_symbol="k", meaning="The rate of the exponential factor."),
    )
    location_in_publication = "Table 5.1, problem 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 40 \c"),),
        expression=r"\param{w} \tmp{u} e^{\param{k} \tmp{u}}",
        interval="[-9, 31]",
        summary=(
            "A function with 1 simple root, growing exponentially in magnitude below that root and, past a minimum at "
            "most 1 above that root, decaying exponentially toward 0."
        ),
        notes=(r"$\param{w}$ and $\param{k}$ are the source's parameters $a$ and $b$.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, w: float, k: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 40.0 * c
        return w * x * math.exp(k * x)

    def interval_bounds(self, w: float, k: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-9.0, 31.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("w", "k"),
                rows=((-40.0, -1.0), (-100.0, -2.0), (-200.0, -3.0)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"w": -40.0, "k": -1.0}, x=3.0, c=0.0, expected=-5.974448204143673),
        FormulaTestCase.value(params={"w": -40.0, "k": -1.0}, x=3.0, c=0.25, expected=307057.2843599684),
        FormulaTestCase.value(params={"w": -100.0, "k": -2.0}, x=3.0, c=0.0, expected=-0.7436256529999076),
        FormulaTestCase.value(params={"w": -200.0, "k": -3.0}, x=3.0, c=0.0, expected=-0.07404588245200773),
        FormulaTestCase.interval_bounds(params={"w": -40.0, "k": -1.0}, expected=(-9.0, 31.0)),
    )
