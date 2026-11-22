"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p14`` in the survey of published test problems.
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


class Burkardt2016P14(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``1.0/((x - 0.3)^2 + 0.01) + 1.0/((x - 0.9)^2 + 0.04) + 2.0*x - 5.2``;
    the formula's intervals are `[-10.0, 10.0]` (rang); `[-0.5, 3.0]` (starts 2 and 1).

    The source's starting points, in order, are `3.0`, `-0.5`, `0.0` and `2.12742`. The code selects the 4th with `i % 3
    == 0`, where the first 3 use `i % 4`, so `p14_start(4)` matches no branch and fails.
    """

    number = (1, 3, 1, 14)
    name = "p14"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p14"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\frac{1.0}{\left(\tmp{u} - 0.3\right)^{2} + 0.01} + \frac{1.0}{\left(\tmp{u} - "
            r"0.9\right)^{2} + 0.04} + 2.0 \tmp{u} - 5.2"
        ),
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 1.0 / ((x - 0.3) ** 2 + 0.01) + 1.0 / ((x - 0.9) ** 2 + 0.04) + 2.0 * x - 5.2

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 10.0, 20.0), (-0.5, 3.0, 3.5)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=-13.104365904365904
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.25, expected=-23.178240428234975
        ),
        FormulaTestCase.value(params={"a": -0.5, "b": 3.0, "c_scale": 3.5}, x=0.55, c=0.0, expected=15.846949602122013),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -0.5, "b": 3.0, "c_scale": 3.5}, expected=(-0.5, 3.0)),
    )
