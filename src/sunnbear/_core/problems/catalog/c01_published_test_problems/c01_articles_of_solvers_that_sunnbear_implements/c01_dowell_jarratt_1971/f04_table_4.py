"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 4`` in the survey of published test problems.
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


class DowellJarratt1971Table4(Formula):
    """This formula comes from Dowell, Jarratt (1971).

    The survey writes the source's function as ``x^2 - (1 - x)^n``, with the parameters ``n = 2, 5, 15, 20``; the
    formula's interval is ``[0, 1]``.

    The caption says the function has 1 inflection point on `[0, 1]`.
    """

    number = (1, 1, 1, 4)
    name = "Table 4"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Table 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} - \left(1 - \tmp{u}\right)^{\param{n}}",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - (1 - x) ** n

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",), rows=((2.0,), (5.0,), (15.0,), (20.0,)), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.25, expected=-0.9),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=-0.07807000000000001),
        FormulaTestCase.value(params={"n": 15.0}, x=0.3, c=0.0, expected=0.085252438490057),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=0.08920207733702387),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
