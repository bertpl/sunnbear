"""This module holds a formula of Li, Zhou, Lange, Tian (2026).

The formula comes from the row with the key ``Ex. 1`` in the survey of published test problems.
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


class LiZhouLangeTian2026Example1(Formula):
    """This formula comes from Li, Zhou, Lange, Tian (2026).

    The survey writes the source's function as ``cos(0.5*pi*x) - x``; the formula's intervals are `x` in R; starting
    values `x(0) = -1, 2`; `[-2, 1]` (Figure 1(a)); `[0, 4]` (Figure 1(b)).

    Stated root `0.594612`. Table 1, Fig. 1.
    """

    number = (1, 2, 20, 1)
    name = "Example 1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Example 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\cos{\left(0.5 \pi \tmp{u} \right)} - \tmp{u}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function with 1 simple root and, on each interval, 2 local extrema whose values are all at least 0.78 "
            "away from 0."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.cos(0.5 * math.pi * x) - x

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-2.0, 1.0, 3.0), (0.0, 4.0, 4.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -2.0, "b": 1.0, "c_scale": 3.0}, x=-1.1, c=0.0, expected=0.9435655349597691),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 1.0, "c_scale": 3.0}, x=-1.1, c=0.25, expected=0.8776300796023234
        ),
        FormulaTestCase.value(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, x=1.2, c=0.0, expected=-1.5090169943749474),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 1.0, "c_scale": 3.0}, expected=(-2.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, expected=(0.0, 4.0)),
    )
