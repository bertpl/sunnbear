"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.10`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021WellBehavedFunction10(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``(x + 2/3)/(x + 101/100)``; the formula's interval is ``[-1, 1]``.

    Table 1 names it "Poly.Frac."; the authors' MATLAB code calls it "Polynomial Fraction".
    """

    number = (1, 1, 9, 9)
    name = "Well-behaved function 10"
    params = ()
    location_in_publication = "Table 1, well-behaved function 10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\frac{\tmp{u} + \frac{2}{3}}{\tmp{u} + \frac{101}{100}}",
        interval="[-1, 1]",
        summary=(
            "A ratio of 2 lines with 1 simple root 0.34 above a pole below the lower bound, and steepest next to that "
            "bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x + 2 / 3) / (x + 101 / 100)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=0.4371584699453552),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-2.121212121212122),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
