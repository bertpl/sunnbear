"""This module holds a formula of Norton (1985).

The formula comes from the row with the key ``10`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Norton1985Function10(Formula):
    """This formula comes from Norton (1985).

    The survey writes the source's function as ``x^n + a*x + b``, with the parameters `a = 1, b = 10^-4`; `n = 3, 5, 9,
    19`; the formula's interval is ``[-0.7, 1]``.

    Group II.
    """

    number = (1, 2, 2, 6)
    name = "Function 10"
    params = (
        FormulaParam("w1", latex_symbol="w_1", meaning=r"The coefficient of $\tmp{u}$."),
        FormulaParam("w2", latex_symbol="w_2", meaning="The constant term."),
        FormulaParam("n", latex_symbol="n"),
    )
    location_in_publication = "Section 4, function 10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.7 \c"),),
        expression=r"\tmp{u}^{\param{n}} + \param{w1} \tmp{u} + \param{w2}",
        interval="[-0.7, 1]",
        summary=(
            r"An increasing function with 1 simple root only $10^{-4}$ below an inflection point where the derivatives "
            r"of order 2 to $\param{n} - 1$ are all 0."
        ),
        notes=(r"$\param{w1}$ and $\param{w2}$ are the source's parameters $a$ and $b$.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, w1: float, w2: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.7 * c
        return x**n + w1 * x + w2

    def interval_bounds(self, w1: float, w2: float, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.7, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("w1", "w2", "n"),
                rows=((1.0, 0.0001, 3.0), (1.0, 0.0001, 5.0), (1.0, 0.0001, 9.0), (1.0, 0.0001, 19.0)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"w1": 1.0, "w2": 0.0001, "n": 3.0}, x=-0.19, c=0.0, expected=-0.196759),
        FormulaTestCase.value(params={"w1": 1.0, "w2": 0.0001, "n": 3.0}, x=-0.19, c=0.25, expected=-0.847508375),
        FormulaTestCase.value(
            params={"w1": 1.0, "w2": 0.0001, "n": 5.0}, x=-0.19, c=0.0, expected=-0.19014760990000001
        ),
        FormulaTestCase.value(
            params={"w1": 1.0, "w2": 0.0001, "n": 9.0}, x=-0.19, c=0.0, expected=-0.18990032268769777
        ),
        FormulaTestCase.value(
            params={"w1": 1.0, "w2": 0.0001, "n": 19.0}, x=-0.19, c=0.0, expected=-0.18990000000001978
        ),
        FormulaTestCase.interval_bounds(params={"w1": 1.0, "w2": 0.0001, "n": 3.0}, expected=(-0.7, 1.0)),
    )
