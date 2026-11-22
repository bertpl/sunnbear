"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``I.5`` in the survey of published test problems.
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


class BusDekker1975Function5(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``(1 + (1 - n)^4)*x - (1 - n*x)^4``, with the parameters ``n = 1, 4, 8``;
    the formula's interval is ``[0, 1]``.

    The article: 1 turning point and 1 inflection point in `[0, 1]`.
    """

    number = (1, 2, 1, 4)
    name = "Function 5"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Group I, function 5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\left(1 + \left(1 - \param{n}\right)^{4}\right) \tmp{u} - \left(1 - \param{n} " r"\tmp{u}\right)^{4}"
        ),
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (1 + (1 - n) ** 4) * x - (1 - n * x) ** 4

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((1.0,), (4.0,), (8.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=0.059899999999999974),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.76450625),
        FormulaTestCase.value(params={"n": 4.0}, x=0.3, c=0.0, expected=24.598399999999998),
        FormulaTestCase.value(params={"n": 8.0}, x=0.3, c=0.0, expected=716.7583999999999),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
