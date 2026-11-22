"""This module holds a formula of Alefeld, Potra (1992).

The formula comes from the row with the key ``6`` in the survey of published test problems.
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


class AlefeldPotra1992Problem6(Formula):
    """This formula comes from Alefeld, Potra (1992).

    The survey writes the source's function as ``(1 + (1 - n)^2)*x^2 - (1 - n*x)^2``, with the parameters ``n = 5, 10,
    20``; the formula's interval is ``[0, 1]``.

    The article writes the first factor in square brackets.
    """

    number = (1, 2, 3, 4)
    name = "Problem 6"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Table 1, problem 6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\left(1 + \left(1 - \param{n}\right)^{2}\right) \tmp{u}^{2} - \left(1 - \param{n} " r"\tmp{u}\right)^{2}"
        ),
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (1 + (1 - n) ** 2) * x**2 - (1 - n * x) ** 2

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((5.0,), (10.0,), (20.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=1.28),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.25, expected=-0.5200000000000001),
        FormulaTestCase.value(params={"n": 10.0}, x=0.3, c=0.0, expected=3.38),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=7.58),
        FormulaTestCase.interval_bounds(params={"n": 5.0}, expected=(0.0, 1.0)),
    )
