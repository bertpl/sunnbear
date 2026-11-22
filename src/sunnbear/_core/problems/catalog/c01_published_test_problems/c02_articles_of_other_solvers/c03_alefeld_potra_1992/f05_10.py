"""This module holds a formula of Alefeld, Potra (1992).

The formula comes from the row with the key ``10`` in the survey of published test problems.
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


class AlefeldPotra199210(Formula):
    """This formula comes from Alefeld, Potra (1992).

    The survey writes the source's function as ``x^2 + sin(x/n) - 1/4``, with the parameters ``n = 5, 10, 20``; the
    formula's interval is ``[0, 1]``.
    """

    number = (1, 2, 3, 5)
    name = "10"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Table 1, problem 10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} + \sin{\left(\frac{\tmp{u}}{\param{n}} \right)} - \frac{1}{4}",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 + math.sin(x / n) - 1 / 4

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((5.0,), (10.0,), (20.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=-0.10003599352055541),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.25, expected=-0.23750016666583335),
        FormulaTestCase.value(params={"n": 10.0}, x=0.3, c=0.0, expected=-0.13000449979750434),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=-0.1450005624936719),
        FormulaTestCase.interval_bounds(params={"n": 5.0}, expected=(0.0, 1.0)),
    )
