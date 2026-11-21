"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``4`` in the survey of published test problems.
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


class Chandrupatla19974(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``6*(x - 2)^5``; the formula's intervals are `[0, 5]`; `[-10, 10]`;
    `[-1E4, 1E4]`; `[-1E6, 1E6]`; `[-1E10, 1E10]`.

    Printed zero: `x = 2`.
    """

    number = (1, 1, 7, 4)
    name = "4"
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
        location="Table 1, function 4",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"6 \left(\tmp{u} - 2\right)^{5}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 6 * (x - 2) ** 5

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (0.0, 5.0, 5.0),
                    (-10.0, 10.0, 20.0),
                    (-10000.0, 10000.0, 20000.0),
                    (-1000000.0, 1000000.0, 2000000.0),
                    (-10000000000.0, 10000000000.0, 20000000000.0),
                ),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=-0.1875),
        FormulaTestCase.value(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.25, expected=-98.478515625),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=-46656.0),
        FormulaTestCase.value(
            params={"a": -10000.0, "b": 10000.0, "c_scale": 20000.0}, x=-4000.0, c=0.0, expected=-6.15937536768192e18
        ),
        FormulaTestCase.value(
            params={"a": -1000000.0, "b": 1000000.0, "c_scale": 2000000.0},
            x=-400000.0,
            c=0.0,
            expected=-6.144153601536008e28,
        ),
        FormulaTestCase.value(
            params={"a": -10000000000.0, "b": 10000000000.0, "c_scale": 20000000000.0},
            x=-4000000000.0,
            c=0.0,
            expected=-6.14400001536e48,
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, expected=(0.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(
            params={"a": -10000.0, "b": 10000.0, "c_scale": 20000.0}, expected=(-10000.0, 10000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1000000.0, "b": 1000000.0, "c_scale": 2000000.0}, expected=(-1000000.0, 1000000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -10000000000.0, "b": 10000000000.0, "c_scale": 20000000000.0},
            expected=(-10000000000.0, 10000000000.0),
        ),
    )
