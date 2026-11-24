"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p11`` in the survey of published test problems.
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


class Burkardt2016ProblemP11(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``(16.0 - x^4)/(16.0*x^4 + epsilon)``, with the parameters ``epsilon =
    0.00001``; the formula's intervals are `[0.0, 10.0]` (rang); `[0.25, 5.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.25`, `5.0` and `1.1`.
    """

    number = (1, 3, 1, 11)
    name = "Problem p11"
    params = (
        FormulaParam("epsilon", latex_symbol=r"\epsilon"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p11"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\frac{16.0 - \tmp{u}^{4}}{16.0 \tmp{u}^{4} + \param{epsilon}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A rational function with 1 root and a narrow peak of $1.6 \cdot 10^{6}$ that lies 2 below the root, "
            r'referred to in the source as "The Pinhead".'
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, epsilon: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (16.0 - x**4) / (16.0 * x**4 + epsilon)

    def interval_bounds(self, epsilon: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("epsilon", "a", "b", "c_scale"),
                rows=((1e-05, 0.0, 10.0, 10.0), (1e-05, 0.25, 5.0, 4.75)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"epsilon": 1e-05, "a": 0.0, "b": 10.0, "c_scale": 10.0},
            x=3.0,
            c=0.0,
            expected=-0.050154320600661106,
        ),
        FormulaTestCase.value(
            params={"epsilon": 1e-05, "a": 0.0, "b": 10.0, "c_scale": 10.0}, x=3.0, c=0.25, expected=15.937340626593734
        ),
        FormulaTestCase.value(
            params={"epsilon": 1e-05, "a": 0.25, "b": 5.0, "c_scale": 4.75},
            x=1.675,
            c=0.0,
            expected=0.06454007368800385,
        ),
        FormulaTestCase.interval_bounds(
            params={"epsilon": 1e-05, "a": 0.0, "b": 10.0, "c_scale": 10.0}, expected=(0.0, 10.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"epsilon": 1e-05, "a": 0.25, "b": 5.0, "c_scale": 4.75}, expected=(0.25, 5.0)
        ),
    )
