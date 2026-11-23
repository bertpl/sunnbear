"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p03`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Burkardt2016ProblemP03(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``x*exp(-x)``; the formula's intervals are `[-10.0, 100.0]` (rang);
    `[-1.0, 0.5]` (starts 1 and 2).

    The source's starting points, in order, are `-1.0`, `0.5` and `2.0`.
    """

    number = (1, 3, 1, 3)
    name = "Problem p03"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p03"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u} e^{- \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
        summary="A function with 1 root, positive but below $10^{-9}$ over most of the wide interval.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x * math.exp(-x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 100.0, 110.0), (-1.0, 0.5, 1.5)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0}, x=23.0, c=0.0, expected=2.3602323152914347e-09
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0}, x=23.0, c=0.25, expected=-405.07709085234814
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 0.5, "c_scale": 1.5}, x=-0.55, c=0.0, expected=-0.9532891598270675
        ),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 100.0, "c_scale": 110.0}, expected=(-10.0, 100.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 0.5, "c_scale": 1.5}, expected=(-1.0, 0.5)),
    )
