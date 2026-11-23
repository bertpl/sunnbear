"""This module holds a formula of Gottlieb, Thompson (2010).

The formula comes from the row with the key ``3`` in the survey of published test problems.
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


class GottliebThompson2010Test3(Formula):
    """This formula comes from Gottlieb, Thompson (2010).

    The survey writes the source's function as ``11*x^11 - 1``; the formula's intervals are `[0.1, 0.9]`; `[0.4, 1]`
    (Figure 1).

    Table 2's root `0.8041330975`.
    """

    number = (1, 2, 8, 2)
    name = "Test 3"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 1, test 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"11 \tmp{u}^{11} - 1",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"An 11th power minus 1, with 1 root, within 0.01 of $-1$ below $\x = 0.52$ and steep toward the upper "
            r"bound of both intervals."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 11 * x**11 - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((0.1, 0.9, 0.8), (0.4, 1.0, 0.6)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.1, "b": 0.9, "c_scale": 0.8}, x=0.34, c=0.0, expected=-0.9999227922719982),
        FormulaTestCase.value(
            params={"a": 0.1, "b": 0.9, "c_scale": 0.8}, x=0.34, c=0.25, expected=-0.9999999955454784
        ),
        FormulaTestCase.value(params={"a": 0.4, "b": 1.0, "c_scale": 0.6}, x=0.58, c=0.0, expected=-0.972514691599818),
        FormulaTestCase.interval_bounds(params={"a": 0.1, "b": 0.9, "c_scale": 0.8}, expected=(0.1, 0.9)),
        FormulaTestCase.interval_bounds(params={"a": 0.4, "b": 1.0, "c_scale": 0.6}, expected=(0.4, 1.0)),
    )
