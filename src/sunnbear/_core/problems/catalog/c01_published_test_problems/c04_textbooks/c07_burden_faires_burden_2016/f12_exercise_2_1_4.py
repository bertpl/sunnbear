"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-4; 2.6-2(g)`` in the survey of published test problems.
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


class BurdenFairesBurden2016Exercise214(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^4 - 2*x^3 - 4*x^2 + 4*x + 4``; the formula's intervals are `[-2,
    -1]`; `[0, 2]`; `[2, 3]`; `[-1, 0]`.

    As 2.1-3.
    """

    number = (1, 4, 7, 12)
    name = "Exercise 2.1-4"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercises 2.1-4, 2.6-2(g)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{4} - 2 \tmp{u}^{3} - 4 \tmp{u}^{2} + 4 \tmp{u} + 4",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A quartic, the product of $\tmp{u}^2 - 2$ and $\tmp{u}^2 - 2\tmp{u} - 2$, with 4 simple roots, 1 on each "
            r"interval."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**4 - 2 * x**3 - 4 * x**2 + 4 * x + 4

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-2.0, -1.0, 1.0), (0.0, 2.0, 2.0), (2.0, 3.0, 1.0), (-1.0, 0.0, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -2.0, "b": -1.0, "c_scale": 1.0}, x=-1.7, c=0.0, expected=3.818099999999999),
        FormulaTestCase.value(
            params={"a": -2.0, "b": -1.0, "c_scale": 1.0}, x=-1.7, c=0.25, expected=10.278756249999999
        ),
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.0, expected=4.6576),
        FormulaTestCase.value(params={"a": 2.0, "b": 3.0, "c_scale": 1.0}, x=2.3, c=0.0, expected=-4.309900000000001),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 0.0, "c_scale": 1.0}, x=-0.7, c=0.0, expected=0.16610000000000025
        ),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": -1.0, "c_scale": 1.0}, expected=(-2.0, -1.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, expected=(0.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 3.0, "c_scale": 1.0}, expected=(2.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 0.0, "c_scale": 1.0}, expected=(-1.0, 0.0)),
    )
