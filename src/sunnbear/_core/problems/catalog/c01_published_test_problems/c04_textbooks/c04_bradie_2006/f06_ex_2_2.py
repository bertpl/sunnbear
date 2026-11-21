"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``Ex. 2.2; Fig. 2.3; Tables 2.2, 2.3, 2.5; §2.2 (p. 74); §2.4 (pp. 98, 100);
§2.5 (p. 109); 2.1-13; 2.5-15; 2.6-3`` in the survey of published test problems.
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


class Bradie2006Ex22(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``tan(pi*x) - x - 6``; the formula's intervals are `(0.40, 0.48)`; `[0,
    0.48]` (§2.4, p. 100); `[0, 0.5]` (Fig. 2.3).

    The second standard test problem: infinitely many roots; the smallest positive one is `0.4510472588`. `tan(pi*x)`
    has a pole at `x = 0.5`, the right bound of Fig. 2.3's interval. Bisection and false position on `(0.40, 0.48)` (Ex.
    2.2, Tables 2.2, 2.3, p. 74; Aitken on the false-position sequence in 2.6-3). Newton from `p0 = 0.48` converges in 5
    iterations; from `p0 = 0.4` it does not converge in 5000; from `p0 = 0` it converges to the root `697.4995475` (p.
    98). Secant from `p0 = 0.4, p1 = 0.48` (p. 109) and from `(0, 0.48)`, `(0.24, 0.48)`, `(0.4, 0.48)` (2.5-15). 2.1-13
    seeks the next smallest positive root.
    """

    number = (1, 4, 4, 6)
    name = "Ex. 2.2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location=(
            "Example 2.2; Fig. 2.3; Tables 2.2, 2.3, 2.5; §2.2 (p. 74); §2.4 (pp. 98, 100); §2.5 (p. "
            "109); Exercises 2.1-13, 2.5-15, 2.6-3"
        ),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tan{\left(\pi \tmp{u} \right)} - \tmp{u} - 6",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.tan(math.pi * x) - x - 6

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.4, 0.48, 0.08), (0.0, 0.48, 0.48), (0.0, 0.5, 0.5)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.4, "b": 0.48, "c_scale": 0.08}, x=0.424, c=0.0, expected=-2.315603156282293
        ),
        FormulaTestCase.value(
            params={"a": 0.4, "b": 0.48, "c_scale": 0.08}, x=0.424, c=0.25, expected=-3.189417921365977
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 0.48, "c_scale": 0.48}, x=0.144, c=0.0, expected=-5.657994647140798
        ),
        FormulaTestCase.value(params={"a": 0.0, "b": 0.5, "c_scale": 0.5}, x=0.15, c=0.0, expected=-5.640474550505571),
        FormulaTestCase.interval_bounds(params={"a": 0.4, "b": 0.48, "c_scale": 0.08}, expected=(0.4, 0.48)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 0.48, "c_scale": 0.48}, expected=(0.0, 0.48)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 0.5, "c_scale": 0.5}, expected=(0.0, 0.5)),
    )
