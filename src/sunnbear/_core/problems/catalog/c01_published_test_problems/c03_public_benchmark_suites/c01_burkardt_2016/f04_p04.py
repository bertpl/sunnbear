"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p04`` in the survey of published test problems.
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


class Burkardt2016P04(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 1.0/(100.0*x*x)``; the formula's intervals are `[0.00001,
    20.0]` (rang); `[0.03, 1.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.03` and `1.0`.
    """

    number = (1, 3, 1, 4)
    name = "p04"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p04"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\tmp{u}} - \frac{1.0}{100.0 \tmp{u} \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x) - 1.0 / (100.0 * x * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((1e-05, 20.0, 20.0), (0.03, 1.0, 0.97)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, x=6.00001, c=0.0, expected=403.43255002398956
        ),
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, x=6.00001, c=0.25, expected=2.7083092114102434
        ),
        FormulaTestCase.value(
            params={"a": 0.03, "b": 1.0, "c_scale": 0.97}, x=0.321, c=0.0, expected=1.2814568333078415
        ),
        FormulaTestCase.interval_bounds(params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, expected=(1e-05, 20.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.03, "b": 1.0, "c_scale": 0.97}, expected=(0.03, 1.0)),
    )
