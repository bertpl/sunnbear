"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§1.1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Moler200411(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``1/x - (x - 1)``; the formula's interval is `[0, 4]` (Figure 1.2).

    The aspect ratio equation `1/x = x - 1` of the golden rectangle, whose positive root is the golden ratio `(1 +
    sqrt(5))/2`. Besides the quadratic formula, §1.1 solves it 3 ways in MATLAB: as the polynomial `x^2 - x - 1` with
    `roots`; symbolically with `solve(1/x == x-1)`; and as `f = @(x) 1./x-(x-1)` with `fzero(f,1)`, from the starting
    point `x = 1`. `ezplot(f,0,4)` plots `f` on `[0, 4]` (Figure 1.2), where it becomes infinite as `x` tends to 0.
    """

    number = (1, 4, 3, 1)
    name = "§1.1"
    params = ()
    location_in_publication = "§1.1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"\frac{1}{\tmp{u}} - \left(\tmp{u} - 1\right)",
        interval="[0, 4]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return 1 / x - (x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.2, c=0.0, expected=0.6333333333333334),
        FormulaTestCase.value(params={}, x=1.2, c=0.25, expected=5.800000000000002),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 4.0)),
    )
