"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-6(d)`` in the survey of published test problems.
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


class BurdenFairesBurden2016Exercise236D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``(x - 2)^2 - log(x)``; the formula's intervals are `[1, 2]`; `[e, 4]`.

    The value ``e`` is rounded to 12 significant digits, the most that a parameter value holds.

    As 2.3-6(a).
    """

    number = (1, 4, 7, 36)
    name = "Exercise 2.3-6(d)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercise 2.3-6(d)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\tmp{u} - 2\right)^{2} - \ln{\left(\tmp{u} \right)}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A convex function with 1 simple root on each published interval and a minimum of $-0.75$ between those 2 "
            "roots."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x - 2) ** 2 - math.log(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((1.0, 2.0, 1.0), (2.71828182846, 4.0, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.0, expected=0.22763573553250885),
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.25, expected=0.8537098358305679),
        FormulaTestCase.value(
            params={"a": 2.71828182846, "b": 4.0, "c_scale": 1.0}, x=3.1028, c=0.0, expected=0.08386291036542012
        ),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, expected=(1.0, 2.0)),
        FormulaTestCase.interval_bounds(
            params={"a": 2.71828182846, "b": 4.0, "c_scale": 1.0}, expected=(2.71828182846, 4.0)
        ),
    )
