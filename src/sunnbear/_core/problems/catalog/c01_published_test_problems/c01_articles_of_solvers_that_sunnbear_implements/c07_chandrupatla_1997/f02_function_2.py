"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``2`` in the survey of published test problems.
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


class Chandrupatla1997Function2(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``1 - 1/x^2``; the formula's intervals are `[0.5, 1.51]`; `[1E-4, 1E4]`;
    `[1E-6, 1E6]`; `[1E-10, 1E10]`; `[1E-12, 1E12]`.

    Printed zero: `x = 1`. The article says the author proposed it.
    """

    number = (1, 1, 7, 2)
    name = "Function 2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 1, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"1 - \frac{1}{\tmp{u}^{2}}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 1 - 1 / x**2

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (0.5, 1.51, 1.01),
                    (0.0001, 10000.0, 10000.0),
                    (1e-06, 1000000.0, 1000000.0),
                    (1e-10, 10000000000.0, 10000000000.0),
                    (1e-12, 1000000000000.0, 1000000000000.0),
                ),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.5, "b": 1.51, "c_scale": 1.01}, x=0.803, c=0.0, expected=-0.5508468399169365
        ),
        FormulaTestCase.value(
            params={"a": 0.5, "b": 1.51, "c_scale": 1.01}, x=0.803, c=0.25, expected=-2.29978279179773
        ),
        FormulaTestCase.value(
            params={"a": 0.0001, "b": 10000.0, "c_scale": 10000.0}, x=3000.0, c=0.0, expected=0.9999998888888889
        ),
        FormulaTestCase.value(
            params={"a": 1e-06, "b": 1000000.0, "c_scale": 1000000.0}, x=300000.0, c=0.0, expected=0.9999999999888889
        ),
        FormulaTestCase.value(
            params={"a": 1e-10, "b": 10000000000.0, "c_scale": 10000000000.0}, x=3000000000.0, c=0.0, expected=1.0
        ),
        FormulaTestCase.value(
            params={"a": 1e-12, "b": 1000000000000.0, "c_scale": 1000000000000.0}, x=300000000000.0, c=0.0, expected=1.0
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.5, "b": 1.51, "c_scale": 1.01}, expected=(0.5, 1.51)),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0001, "b": 10000.0, "c_scale": 10000.0}, expected=(0.0001, 10000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-06, "b": 1000000.0, "c_scale": 1000000.0}, expected=(1e-06, 1000000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-10, "b": 10000000000.0, "c_scale": 10000000000.0}, expected=(1e-10, 10000000000.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-12, "b": 1000000000000.0, "c_scale": 1000000000000.0}, expected=(1e-12, 1000000000000.0)
        ),
    )
