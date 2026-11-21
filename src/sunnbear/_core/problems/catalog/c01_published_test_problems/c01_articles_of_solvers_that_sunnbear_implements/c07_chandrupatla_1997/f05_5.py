"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``5`` in the survey of published test problems.
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


class Chandrupatla19975(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``x^9``; the formula's intervals are `[-1, 4]`; `[-2, 5]`; `[-1, 10]`;
    `[-5, 50]`; `[-10, 100]`.

    Printed zero: `x = 0`.
    """

    number = (1, 1, 7, 5)
    name = "5"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="Table 1, function 5",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{9}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**9

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (-1.0, 4.0, 5.0),
                    (-2.0, 5.0, 7.0),
                    (-1.0, 10.0, 11.0),
                    (-5.0, 50.0, 55.0),
                    (-10.0, 100.0, 110.0),
                ),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.0, expected=0.001953125),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.25, expected=-0.07508468627929688
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 5.0, "c_scale": 7.0}, x=0.1, c=0.0, expected=1.0000000000000005e-09
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 10.0, "c_scale": 11.0}, x=2.3, c=0.0, expected=1801.1526614629988
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 50.0, "c_scale": 55.0}, x=11.5, c=0.0, expected=3517876291.919922
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0}, x=23.0, c=0.0, expected=1801152661463.0
        ),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 5.0, "c_scale": 7.0}, expected=(-2.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 10.0, "c_scale": 11.0}, expected=(-1.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 50.0, "c_scale": 55.0}, expected=(-5.0, 50.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 100.0, "c_scale": 110.0}, expected=(-10.0, 100.0)),
    )
