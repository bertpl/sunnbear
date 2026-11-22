"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 7`` in the survey of published test problems.
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


class DowellJarratt1971Table7(Formula):
    """This formula comes from Dowell, Jarratt (1971).

    The survey writes the source's function as ``(n*x - 1)/((n - 1)*x)``, with the parameters ``n = 2, 5, 15, 20``; the
    formula's interval is ``[0.01, 1]``.

    The caption says the y-axis is an asymptote. Starting values `x0 = 0.01`, `x1 = 1.0`.
    """

    number = (1, 1, 1, 7)
    name = "Table 7"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Table 7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.99 \c"),),
        expression=r"\frac{\param{n} \tmp{u} - 1}{\left(\param{n} - 1\right) \tmp{u}}",
        interval="[0.01, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.99 * c
        return (n * x - 1) / ((n - 1) * x)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",), rows=((2.0,), (5.0,), (15.0,), (20.0,)), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.307, c=0.0, expected=-1.2573289902280131),
        FormulaTestCase.value(params={"n": 2.0}, x=0.307, c=0.25, expected=-14.806722689075631),
        FormulaTestCase.value(params={"n": 5.0}, x=0.307, c=0.0, expected=0.4356677524429967),
        FormulaTestCase.value(params={"n": 15.0}, x=0.307, c=0.0, expected=0.8387622149837134),
        FormulaTestCase.value(params={"n": 20.0}, x=0.307, c=0.0, expected=0.8811932110406309),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.01, 1.0)),
    )
