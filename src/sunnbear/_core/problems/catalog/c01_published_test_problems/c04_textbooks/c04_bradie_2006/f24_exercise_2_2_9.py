"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.2-9; 2.4-10; 2.5-10`` in the survey of published test problems.
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


class Bradie2006Exercise229(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^4 - 18*x^2 + 45``; the formula's intervals are `(1, 2)`; `(3, 4)`.

    Roots `sqrt(3)` and `sqrt(15)`. False position, Newton from `p0 = 1` and secant from `p0 = 1, p1 = 2` toward
    `sqrt(3)`; the exercises compare the order of convergence at the 2 roots.
    """

    number = (1, 4, 4, 24)
    name = "Exercise 2.2-9"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercises 2.2-9, 2.4-10, 2.5-10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{4} - 18 \tmp{u}^{2} + 45",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"An even quartic with 1 simple root on each interval, the lower root at an inflection point and the upper "
            r"root right of a local minimum at the bound $\x = 3$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**4 - 18 * x**2 + 45

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((1.0, 2.0, 1.0), (3.0, 4.0, 1.0)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.0, expected=17.4361),
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.25, expected=26.37050625),
        FormulaTestCase.value(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.0, expected=-32.4279),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, expected=(1.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, expected=(3.0, 4.0)),
    )
