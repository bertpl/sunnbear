"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p07`` in the survey of published test problems.
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


class Burkardt2016ProblemP07(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``x^3``; the formula's intervals are `[-1000.0, 999.0]` (rang);
    `[-1000.0, 1.0]` (starts 2 and 1).

    The source's starting points, in order, are `1.0` and `-1000.0`.
    """

    number = (1, 3, 1, 7)
    name = "Problem p07"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p07"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{3}",
        interval=r"[\param{a}, \param{b}]",
        summary="A cube, flat at its triple root and steep far from that root, on intervals about 1000 and 2000 wide.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**3

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1000.0, 999.0, 2000.0), (-1000.0, 1.0, 1000.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 999.0, "c_scale": 2000.0}, x=-400.3, c=0.0, expected=-64144108.027
        ),
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 999.0, "c_scale": 2000.0}, x=-400.3, c=0.25, expected=-729729243.0269998
        ),
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 1.0, "c_scale": 1000.0}, x=-699.7, c=0.0, expected=-342559188.97300005
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1000.0, "b": 999.0, "c_scale": 2000.0}, expected=(-1000.0, 999.0)
        ),
        FormulaTestCase.interval_bounds(params={"a": -1000.0, "b": 1.0, "c_scale": 1000.0}, expected=(-1000.0, 1.0)),
    )
