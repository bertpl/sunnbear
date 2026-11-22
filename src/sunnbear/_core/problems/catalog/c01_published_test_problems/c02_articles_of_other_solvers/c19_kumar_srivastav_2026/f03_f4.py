"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``f4`` in the survey of published test problems.
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


class KumarSrivastav2026F4(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``(x - x*)^3 + 0.05*(x - x*)``, with the parameters ``x* = 0.6``; the
    formula's interval is ``[0, 1]``.

    The formula's parameter ``x_star`` is the source's ``x*``, the stated root.
    """

    number = (1, 2, 19, 3)
    name = "f4"
    params = (FormulaParam("x_star", latex_symbol="x^*"),)
    location_in_publication = "Table 3, f4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"(\tmp{u} - \param{x_star})^3 + 0.05 (\tmp{u} - \param{x_star})",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, x_star: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x - x_star) ** 3 + 0.05 * (x - x_star)

    def interval_bounds(self, x_star: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("x_star",), rows=((0.6,),), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"x_star": 0.6}, x=0.3, c=0.0, expected=-0.041999999999999996),
        FormulaTestCase.value(params={"x_star": 0.6}, x=0.3, c=0.25, expected=-0.193875),
        FormulaTestCase.interval_bounds(params={"x_star": 0.6}, expected=(0.0, 1.0)),
    )
