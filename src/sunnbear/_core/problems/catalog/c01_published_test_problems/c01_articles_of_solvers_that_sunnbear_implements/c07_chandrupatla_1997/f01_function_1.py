"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``1`` in the survey of published test problems.
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


class Chandrupatla1997Function1(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``x^3 - 2*x - 5``; the formula's intervals are `[2, 3]`; `[1, 10]`; `[1,
    100]`; `[-1E4, 1E4]`; `[-1E10, 1E10]`.

    Printed zero: `x = 2.0945515`. The article calls it "extensively tried out in the literature". Its appendix program
    evaluates this function.
    """

    number = (1, 1, 7, 1)
    name = "Function 1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 1, function 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{3} - 2 \tmp{u} - 5",
        interval=r"[\param{a}, \param{b}]",
        summary="A cubic with 1 real root, whose 2 local extrema, both below 0, lie only in the 2 widest intervals.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**3 - 2 * x - 5

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (2.0, 3.0, 1.0),
                    (1.0, 10.0, 9.0),
                    (1.0, 100.0, 99.0),
                    (-10000.0, 10000.0, 20000.0),
                    (-10000000000.0, 10000000000.0, 20000000000.0),
                ),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 2.0, "b": 3.0, "c_scale": 1.0}, x=2.3, c=0.0, expected=2.5669999999999975),
        FormulaTestCase.value(params={"a": 2.0, "b": 3.0, "c_scale": 1.0}, x=2.3, c=0.25, expected=-0.4848750000000019),
        FormulaTestCase.value(params={"a": 1.0, "b": 10.0, "c_scale": 9.0}, x=3.7, c=0.0, expected=38.25300000000001),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 100.0, "c_scale": 99.0}, x=30.7, c=0.0, expected=28868.042999999998
        ),
        FormulaTestCase.value(
            params={"a": -10000.0, "b": 10000.0, "c_scale": 20000.0}, x=-4000.0, c=0.0, expected=-63999992005.0
        ),
        FormulaTestCase.value(
            params={"a": -10000000000.0, "b": 10000000000.0, "c_scale": 20000000000.0},
            x=-4000000000.0,
            c=0.0,
            expected=-6.4e28,
        ),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 3.0, "c_scale": 1.0}, expected=(2.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 10.0, "c_scale": 9.0}, expected=(1.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 100.0, "c_scale": 99.0}, expected=(1.0, 100.0)),
        FormulaTestCase.interval_bounds(
            params={"a": -10000.0, "b": 10000.0, "c_scale": 20000.0}, expected=(-10000.0, 10000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -10000000000.0, "b": 10000000000.0, "c_scale": 20000000000.0},
            expected=(-10000000000.0, 10000000000.0),
        ),
    )
