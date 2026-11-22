"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Ex. 5.2; Fig. 5.4`` in the survey of published test problems.
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


class ChapraCanale2015Ex52(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``sin(10*x) + cos(3*x)``; the formula's intervals are `[0, 5]`; `[3, 5]`
    (Fig. 5.4(b)); `[4.2, 4.3]` (Fig. 5.4(c)).

    Several roots on the interval. Plots on narrower ranges (Fig. 5.4) show that the apparent double root near 4.2 is 2
    distinct roots, at about 4.23 and 4.26.
    """

    number = (1, 4, 6, 2)
    name = "Ex. 5.2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Example 5.2; Fig. 5.4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\sin{\left(10 \tmp{u} \right)} + \cos{\left(3 \tmp{u} \right)}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(10 * x) + math.cos(3 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 5.0, 5.0), (3.0, 5.0, 2.0), (4.2, 4.3, 0.1)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=0.4394920407263372),
        FormulaTestCase.value(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.25, expected=1.3301610129777774),
        FormulaTestCase.value(params={"a": 3.0, "b": 5.0, "c_scale": 2.0}, x=3.6, c=0.0, expected=-1.186108759898451),
        FormulaTestCase.value(
            params={"a": 4.2, "b": 4.3, "c_scale": 0.1}, x=4.23, c=0.0, expected=-0.0014226045479633668
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, expected=(0.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": 3.0, "b": 5.0, "c_scale": 2.0}, expected=(3.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": 4.2, "b": 4.3, "c_scale": 0.1}, expected=(4.2, 4.3)),
    )
