"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-12`` in the survey of published test problems.
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


class BurdenFairesBurden2016Exercise2112(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``(x + 2)*(x + 1)^2*x*(x - 1)^3*(x - 2)``; the formula's intervals are
    `[-1.5, 2.5]`; `[-0.5, 2.4]`; `[-0.5, 3]`; `[-3, -0.5]`.

    As 2.1-11, with -1 a double zero.
    """

    number = (1, 4, 7, 23)
    name = "Exercise 2.1-12"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercise 2.1-12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\left(\tmp{u} + 2\right) \left(\tmp{u} + 1\right)^{2} \tmp{u} \left(\tmp{u} - 1\right)^{3}"
            r" \left(\tmp{u} - 2\right)"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A polynomial with 5 distinct roots, 1 of them a double root at which the sign does not change, and 1 to 4 "
            "of the 5 on each interval."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x + 2) * (x + 1) ** 2 * x * (x - 1) ** 3 * (x - 2)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1.5, 2.5, 4.0), (-0.5, 2.4, 2.9), (-0.5, 3.0, 3.5), (-3.0, -0.5, 2.5)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -1.5, "b": 2.5, "c_scale": 4.0}, x=-0.3, c=0.0, expected=-1.26276969),
        FormulaTestCase.value(
            params={"a": -1.5, "b": 2.5, "c_scale": 4.0}, x=-0.3, c=0.25, expected=-3.288375090000001
        ),
        FormulaTestCase.value(params={"a": -0.5, "b": 2.4, "c_scale": 2.9}, x=0.37, c=0.0, expected=0.6708114349200621),
        FormulaTestCase.value(params={"a": -0.5, "b": 3.0, "c_scale": 3.5}, x=0.55, c=0.0, expected=0.4452170726953124),
        FormulaTestCase.value(
            params={"a": -3.0, "b": -0.5, "c_scale": 2.5}, x=-2.25, c=0.0, expected=128.2276153564453
        ),
        FormulaTestCase.interval_bounds(params={"a": -1.5, "b": 2.5, "c_scale": 4.0}, expected=(-1.5, 2.5)),
        FormulaTestCase.interval_bounds(params={"a": -0.5, "b": 2.4, "c_scale": 2.9}, expected=(-0.5, 2.4)),
        FormulaTestCase.interval_bounds(params={"a": -0.5, "b": 3.0, "c_scale": 3.5}, expected=(-0.5, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": -0.5, "c_scale": 2.5}, expected=(-3.0, -0.5)),
    )
