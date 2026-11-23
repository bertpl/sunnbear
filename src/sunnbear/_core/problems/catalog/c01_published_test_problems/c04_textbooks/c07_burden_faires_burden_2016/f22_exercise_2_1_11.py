"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-11`` in the survey of published test problems.
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


class BurdenFairesBurden2016Exercise2111(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``(x + 2)*(x + 1)*x*(x - 1)^3*(x - 2)``; the formula's intervals are
    `[-3, 2.5]`; `[-2.5, 3]`; `[-1.75, 1.5]`; `[-1.5, 1.75]`.

    Zeros -2, -1, 0, 1 (triple) and 2; asks to which zero bisection converges on each interval.
    """

    number = (1, 4, 7, 22)
    name = "Exercise 2.1-11"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercise 2.1-11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\left(\tmp{u} + 2\right) \left(\tmp{u} + 1\right) \tmp{u} \left(\tmp{u} - 1\right)^{3} "
            r"\left(\tmp{u} - 2\right)"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A polynomial with 5 roots on the wide intervals and 3 on the narrow ones, among them a triple root, and "
            "below 0.01 in magnitude within 0.11 of that triple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x + 2) * (x + 1) * x * (x - 1) ** 3 * (x - 2)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-3.0, 2.5, 5.5), (-2.5, 3.0, 5.5), (-1.75, 1.5, 3.25), (-1.5, 1.75, 3.25)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -3.0, "b": 2.5, "c_scale": 5.5}, x=-1.35, c=0.0, expected=13.352530028906255
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 2.5, "c_scale": 5.5}, x=-1.35, c=0.25, expected=-832.2891952841128
        ),
        FormulaTestCase.value(
            params={"a": -2.5, "b": 3.0, "c_scale": 5.5}, x=-0.85, c=0.0, expected=-2.6458673695312505
        ),
        FormulaTestCase.value(
            params={"a": -1.75, "b": 1.5, "c_scale": 3.25}, x=-0.775, c=0.0, expected=-3.3149605846618653
        ),
        FormulaTestCase.value(
            params={"a": -1.5, "b": 1.75, "c_scale": 3.25}, x=-0.525, c=0.0, expected=-3.2939412342590333
        ),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": 2.5, "c_scale": 5.5}, expected=(-3.0, 2.5)),
        FormulaTestCase.interval_bounds(params={"a": -2.5, "b": 3.0, "c_scale": 5.5}, expected=(-2.5, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.75, "b": 1.5, "c_scale": 3.25}, expected=(-1.75, 1.5)),
        FormulaTestCase.interval_bounds(params={"a": -1.5, "b": 1.75, "c_scale": 3.25}, expected=(-1.5, 1.75)),
    )
