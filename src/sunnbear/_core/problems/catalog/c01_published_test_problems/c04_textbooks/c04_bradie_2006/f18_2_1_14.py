"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-14`` in the survey of published test problems.
"""

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


class Bradie20062114(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``(x - 0.5)*(x + 1)^3*(x - 2)``; the formula's intervals are `(-3, 3)`;
    `(-1.5, 3)`; `(-2, 4)`; `(-2, 3)`; `(-1.5, 2.2)`; `(-7, 3)`.

    Roots -1 (triple), 0.5 and 2, all inside each interval; asks to which root bisection converges from each.
    """

    number = (1, 4, 4, 18)
    name = "2.1-14"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="Exercise 2.1-14",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\tmp{u} - 0.5\right) \left(\tmp{u} + 1\right)^{3} \left(\tmp{u} - 2\right)",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x - 0.5) * (x + 1) ** 3 * (x - 2)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (-3.0, 3.0, 6.0),
                    (-1.5, 3.0, 4.5),
                    (-2.0, 4.0, 6.0),
                    (-2.0, 3.0, 5.0),
                    (-1.5, 2.2, 3.7),
                    (-7.0, 3.0, 10.0),
                ),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -3.0, "b": 3.0, "c_scale": 6.0}, x=-1.2, c=0.0, expected=-0.04351999999999997
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 3.0, "c_scale": 6.0}, x=-1.2, c=0.25, expected=-73.89152000000003
        ),
        FormulaTestCase.value(params={"a": -1.5, "b": 3.0, "c_scale": 4.5}, x=-0.15, c=0.0, expected=0.8582396875),
        FormulaTestCase.value(params={"a": -2.0, "b": 4.0, "c_scale": 6.0}, x=-0.2, c=0.0, expected=0.78848),
        FormulaTestCase.value(params={"a": -2.0, "b": 3.0, "c_scale": 5.0}, x=-0.5, c=0.0, expected=0.3125),
        FormulaTestCase.value(params={"a": -1.5, "b": 2.2, "c_scale": 3.7}, x=-0.39, c=0.0, expected=0.4828112851),
        FormulaTestCase.value(params={"a": -7.0, "b": 3.0, "c_scale": 10.0}, x=-4.0, c=0.0, expected=-729.0),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": 3.0, "c_scale": 6.0}, expected=(-3.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.5, "b": 3.0, "c_scale": 4.5}, expected=(-1.5, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 4.0, "c_scale": 6.0}, expected=(-2.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 3.0, "c_scale": 5.0}, expected=(-2.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.5, "b": 2.2, "c_scale": 3.7}, expected=(-1.5, 2.2)),
        FormulaTestCase.interval_bounds(params={"a": -7.0, "b": 3.0, "c_scale": 10.0}, expected=(-7.0, 3.0)),
    )
