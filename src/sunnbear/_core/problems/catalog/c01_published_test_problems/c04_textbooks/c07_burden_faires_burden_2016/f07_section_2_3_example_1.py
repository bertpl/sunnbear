"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2.3 Ex. 1–3; Fig. 2.8; Tables 2.3–2.6; 2.5-1(d)`` in the survey of
published test problems.
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


class BurdenFairesBurden2016Section23Example1(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``cos(x) - x``; the formula's intervals are `[0, pi/2]` (Fig. 2.8);
    `[0.5, pi/4]` (false position, Ex. 3).

    The values ``pi/2``, ``pi/4`` are rounded to 12 significant digits, the most that a parameter value holds.

    Root `0.7390851332`, the fixed point of `x = cos(x)`. Fixed-point iteration on `x = cos(x)` (Table 2.3) and Newton
    (Table 2.4), both from `p0 = pi/4`; secant (Ex. 2, Table 2.5) and false position (Ex. 3, Table 2.6), both from `p0 =
    0.5, p1 = pi/4`. 2.5-1(d) applies Aitken's method to the iteration on `x = cos(x)` from `p0 = 0.5`.
    """

    number = (1, 4, 7, 7)
    name = "Section 2.3, example 1"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "§2.3 Examples 1–3; Fig. 2.8; Tables 2.3–2.6; Exercise 2.5-1(d)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\cos{\left(\tmp{u} \right)} - \tmp{u}",
        interval=r"[\param{a}, \param{b}]",
        summary="A decreasing function whose root is the fixed point of the cosine.",
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
                rows=((0.0, 1.57079632679, 1.57), (0.5, 0.785398163397, 0.285)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 1.57079632679, "c_scale": 1.57}, x=0.471239, c=0.0, expected=0.41976747789879676
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 1.57079632679, "c_scale": 1.57}, x=0.471239, c=0.25, expected=0.9181626861874498
        ),
        FormulaTestCase.value(
            params={"a": 0.5, "b": 0.785398163397, "c_scale": 0.285}, x=0.585619, c=0.0, expected=0.2477511147682301
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 1.57079632679, "c_scale": 1.57}, expected=(0.0, 1.57079632679)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.5, "b": 0.785398163397, "c_scale": 0.285}, expected=(0.5, 0.785398163397)
        ),
    )
