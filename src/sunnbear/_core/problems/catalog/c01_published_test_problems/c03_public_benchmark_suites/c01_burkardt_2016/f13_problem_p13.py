"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p13`` in the survey of published test problems.
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


class Burkardt2016ProblemP13(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``slope*(x - 100.0)``, with the parameters ``slope = 0.00000000001``; the
    formula's intervals are `[-10000000000000.0, 10000000000000.0]` (rang); `[-100000000000.0, 100000000.0]` (starts 2
    and 1).

    The `rang` interval is `[-1e13, 1e13]`. The source's starting points, in order, are `100000000.0`, `-100000000000.0`
    and `100000013.0`.
    """

    number = (1, 3, 1, 13)
    name = "Problem p13"
    params = (
        FormulaParam("m", latex_symbol="m", meaning="The line's slope."),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p13"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\param{m} \left(\tmp{u} - 100\right)",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A line so flat that its values stay below $10^{-9}$ in magnitude within 100 of its root, referred to in "
            'the source as "Lazy Boy".'
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, m: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return m * (x - 100.0)

    def interval_bounds(self, m: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("m", "a", "b", "c_scale"),
                rows=(
                    (1e-11, -10000000000000.0, 10000000000000.0, 20000000000000.0),
                    (1e-11, -100000000000.0, 100000000.0, 100000000000.0),
                ),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"m": 1e-11, "a": -10000000000000.0, "b": 10000000000000.0, "c_scale": 20000000000000.0},
            x=-4000000000000.0,
            c=0.0,
            expected=-40.000000001,
        ),
        FormulaTestCase.value(
            params={"m": 1e-11, "a": -10000000000000.0, "b": 10000000000000.0, "c_scale": 20000000000000.0},
            x=-4000000000000.0,
            c=0.25,
            expected=-90.000000001,
        ),
        FormulaTestCase.value(
            params={"m": 1e-11, "a": -100000000000.0, "b": 100000000.0, "c_scale": 100000000000.0},
            x=-69970000000.0,
            c=0.0,
            expected=-0.699700001,
        ),
        FormulaTestCase.interval_bounds(
            params={"m": 1e-11, "a": -10000000000000.0, "b": 10000000000000.0, "c_scale": 20000000000000.0},
            expected=(-10000000000000.0, 10000000000000.0),
        ),
        FormulaTestCase.interval_bounds(
            params={"m": 1e-11, "a": -100000000000.0, "b": 100000000.0, "c_scale": 100000000000.0},
            expected=(-100000000000.0, 100000000.0),
        ),
    )
