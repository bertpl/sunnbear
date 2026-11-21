"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``§7.7.1, Fig. 7.6; Ex. 7.4; §7.7.3, Fig. 7.7`` in the survey of published
test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class ChapraCanale2015771(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``x - cos(x)``; the formula's intervals are `[0, 2]` (Fig. 7.6); `[-10,
    10]` (Fig. 7.7).

    Root 0.739085. Excel: trial and error after a plot on `[0, 2]` (Fig. 7.6), and Goal Seek (Ex. 7.4); Mathcad's `root`
    from `x = 1`, with a plot on `[-10, 10]` (Fig. 7.7).
    """

    number = (1, 4, 6, 4)
    name = "§7.7.1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="§7.7.1, Fig. 7.6; Example 7.4; §7.7.3, Fig. 7.7",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u} - \cos{\left(\tmp{u} \right)}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x - math.cos(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 2.0, 2.0), (-10.0, 10.0, 20.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.0, expected=-0.22533561490967832),
        FormulaTestCase.value(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, x=0.6, c=0.25, expected=-0.8950041652780258),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=-3.346356379136388
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 2.0, "c_scale": 2.0}, expected=(0.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
    )
