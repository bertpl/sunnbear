"""This module holds a formula of Ridders (1979).

The formula comes from the row with the key ``III.1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Ridders1979Iii1(Formula):
    """This formula comes from Ridders (1979).

    The survey writes the source's function as ``x*exp(x) - 10``; the formula's intervals are `[-10, 10]`; `[-100,
    100]`.

    Last printed iterate: `1.745528003`.
    """

    number = (1, 1, 5, 2)
    name = "III.1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "c_scale",
            latex_symbol="s",
            meaning=r"The width $\param{b} - \param{a}$ of the interval, rounded to 3 significant digits.",
        ),
    )
    source = FormulaSource(
        reference=(
            "Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous"
            " function. IEEE Transactions on Circuits and Systems 26(11), 979–980. "
            "https://doi.org/10.1109/TCS.1979.1084580."
        ),
        location="Section III, function 1",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u} e^{\tmp{u}} - 10",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x * math.exp(x) - 10

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 10.0, 20.0), (-100.0, 100.0, 200.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=-10.073262555554937
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.25, expected=-10.00111068823678
        ),
        FormulaTestCase.value(
            params={"a": -100.0, "b": 100.0, "c_scale": 200.0}, x=40.0, c=0.0, expected=9.4154106734808e18
        ),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -100.0, "b": 100.0, "c_scale": 200.0}, expected=(-100.0, 100.0)),
    )
