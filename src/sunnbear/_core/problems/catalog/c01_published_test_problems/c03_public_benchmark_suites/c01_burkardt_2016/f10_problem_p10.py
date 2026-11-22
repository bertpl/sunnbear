"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p10`` in the survey of published test problems.
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


class Burkardt2016ProblemP10(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``20.0*x/(100.0*x*x + 1.0)``; the formula's intervals are `[-10.0, 11.0]`
    (rang); `[-0.14, 1.0]` (starts 2 and 1).

    The source's starting points, in order, are `1.0`, `-0.14` and `0.041`.
    """

    number = (1, 3, 1, 10)
    name = "Problem p10"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\frac{20.0 \tmp{u}}{100.0 \tmp{u} \tmp{u} + 1.0}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 20.0 * x / (100.0 * x * x + 1.0)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 11.0, 21.0), (-0.14, 1.0, 1.14)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 11.0, "c_scale": 21.0}, x=-3.7, c=0.0, expected=-0.05401459854014598
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 11.0, "c_scale": 21.0}, x=-3.7, c=0.25, expected=-0.022343579341550946
        ),
        FormulaTestCase.value(
            params={"a": -0.14, "b": 1.0, "c_scale": 1.14}, x=0.202, c=0.0, expected=0.7952129753562711
        ),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 11.0, "c_scale": 21.0}, expected=(-10.0, 11.0)),
        FormulaTestCase.interval_bounds(params={"a": -0.14, "b": 1.0, "c_scale": 1.14}, expected=(-0.14, 1.0)),
    )
