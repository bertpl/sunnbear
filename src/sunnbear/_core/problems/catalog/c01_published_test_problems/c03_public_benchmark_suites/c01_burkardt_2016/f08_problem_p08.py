"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p08`` in the survey of published test problems.
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


class Burkardt2016ProblemP08(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``cos(x) - x``; the formula's intervals are `[-10.0, 10.0]` (rang);
    `[0.5, 1.0]` (starts 2 and 1).

    The source's starting points, in order, are `1.0`, `0.5` and `-1.6`.
    """

    number = (1, 3, 1, 8)
    name = "Problem p08"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p08"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} - \tmp{u}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.cos(x) - x

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 10.0, 20.0), (0.5, 1.0, 0.5)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=3.346356379136388
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.25, expected=8.088869738115323
        ),
        FormulaTestCase.value(params={"a": 0.5, "b": 1.0, "c_scale": 0.5}, x=0.65, c=0.0, expected=0.1460837985490558),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.5, "b": 1.0, "c_scale": 0.5}, expected=(0.5, 1.0)),
    )
