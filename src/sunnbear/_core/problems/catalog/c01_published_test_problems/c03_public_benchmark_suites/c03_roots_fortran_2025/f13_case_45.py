"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``45`` in the survey of published test problems.
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


class RootsFortran2025Case45(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(n*x - 1.0)/((n - 1.0)*x)``, with the parameters ``n = 20, 30``; the
    formula's interval is ``[0.01, 1]``.

    the comment calls it case 11 from "Algorithm 748: Enclosing Zeros of Continuous Functions", with n = 20;
    Alefeld–Potra–Shi (1995) give that function at n = 2, 5, 15 and 20, so n = 30 is roots-fortran's own
    """

    number = (1, 3, 3, 13)
    name = "Case 45"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "root_tests.f90, case 45"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.99 \c"),),
        expression=r"\frac{\param{n} \tmp{u} - 1.0}{\left(\param{n} - 1.0\right) \tmp{u}}",
        interval="[0.01, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.99 * c
        return (n * x - 1.0) / ((n - 1.0) * x)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((20.0,), (30.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"n": 20.0}, x=0.307, c=0.0, expected=0.8811932110406309),
        FormulaTestCase.value(params={"n": 20.0}, x=0.307, c=0.25, expected=0.16806722689075626),
        FormulaTestCase.value(params={"n": 30.0}, x=0.307, c=0.0, expected=0.9221610693024823),
        FormulaTestCase.interval_bounds(params={"n": 20.0}, expected=(0.01, 1.0)),
    )
