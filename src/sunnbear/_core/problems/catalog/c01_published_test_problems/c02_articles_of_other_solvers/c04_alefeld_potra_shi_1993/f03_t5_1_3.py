"""This module holds a formula of Alefeld, Potra, Shi (1993).

The formula comes from the row with the key ``T5.1-3`` in the survey of published test problems.
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


class AlefeldPotraShi1993T513(Formula):
    """This formula comes from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``a*x*exp(b*x)``, with the parameters `a = -40, b = -1`; `a = -100, b =
    -2`; `a = -200, b = -3`; the formula's interval is ``[-9, 31]``.

    The formula's parameters ``a_`` and ``b_`` are the source's ``a`` and ``b``, renamed because ``[a, b]`` names the
    formula's interval.

    Here `a` and `b` are the function's parameters, not the interval's endpoints.
    """

    number = (1, 2, 4, 3)
    name = "T5.1-3"
    params = (
        FormulaParam("a_", latex_symbol="a"),
        FormulaParam("b_", latex_symbol="b"),
    )
    source = FormulaSource(
        reference=(
            "Alefeld, G., Potra, F. A., Shi, Y. (1993). On enclosing simple roots of nonlinear "
            "equations. Mathematics of Computation 61(204), 733–744. "
            "https://doi.org/10.1090/s0025-5718-1993-1192965-2."
        ),
        location="Table 5.1, problem 3",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 40 \c"),),
        expression=r"\param{a_} \tmp{u} e^{\param{b_} \tmp{u}}",
        interval="[-9, 31]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, b_: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 40.0 * c
        return a_ * x * math.exp(b_ * x)

    def interval_bounds(self, a_: float, b_: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-9.0, 31.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a_", "b_"),
                rows=((-40.0, -1.0), (-100.0, -2.0), (-200.0, -3.0)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a_": -40.0, "b_": -1.0}, x=3.0, c=0.0, expected=-5.974448204143673),
        FormulaTestCase.value(params={"a_": -40.0, "b_": -1.0}, x=3.0, c=0.25, expected=307057.2843599684),
        FormulaTestCase.value(params={"a_": -100.0, "b_": -2.0}, x=3.0, c=0.0, expected=-0.7436256529999076),
        FormulaTestCase.value(params={"a_": -200.0, "b_": -3.0}, x=3.0, c=0.0, expected=-0.07404588245200773),
        FormulaTestCase.interval_bounds(params={"a_": -40.0, "b_": -1.0}, expected=(-9.0, 31.0)),
    )
