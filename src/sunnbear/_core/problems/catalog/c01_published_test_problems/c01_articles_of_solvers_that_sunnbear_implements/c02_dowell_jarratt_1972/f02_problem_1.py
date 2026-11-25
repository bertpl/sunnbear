"""This module holds a formula of Dowell, Jarratt (1972).

The formula comes from the row with the key ``Problem 1`` in the survey of published test problems.
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


class DowellJarratt1972Problem1(Formula):
    """This formula comes from Dowell, Jarratt (1972).

    The survey writes the source's function as ``(N*x - 1)/((N - 1)*x)``, with the parameters ``N = 2, 10, 20``; the
    formula's interval is ``[0.01, 1]``.

    Starting values `x0 = 0.01`, `x1 = 1.0`. The article chose it to show the slow convergence of Regula Falsi.
    """

    number = (1, 1, 2, 2)
    name = "Problem 1"
    params = (FormulaParam("N", latex_symbol="N"),)
    location_in_publication = "Problem 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\frac{\param{N} \tmp{u} - 1}{\left(\param{N} - 1\right) \tmp{u}}",
        interval="[0.01, 1]",
        summary=(
            r"A hyperbola, steepest at the lower bound because of a pole below that bound, with 1 root that nears the "
            r"pole as $\param{N}$ grows."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, N: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (N * x - 1) / ((N - 1) * x)

    def interval_bounds(self, N: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("N",), rows=((2.0,), (10.0,), (20.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"N": 2.0}, x=0.307, c=0.0, expected=-1.2573289902280131),
        FormulaTestCase.value(params={"N": 2.0}, x=0.307, c=0.2475, expected=-14.806722689075631),
        FormulaTestCase.value(params={"N": 10.0}, x=0.307, c=0.0, expected=0.749185667752443),
        FormulaTestCase.value(params={"N": 20.0}, x=0.307, c=0.0, expected=0.8811932110406309),
        FormulaTestCase.interval_bounds(params={"N": 2.0}, expected=(0.01, 1.0)),
    )
