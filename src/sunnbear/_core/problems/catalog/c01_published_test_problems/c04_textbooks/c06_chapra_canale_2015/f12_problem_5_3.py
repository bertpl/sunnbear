"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem53(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``-25 + 82*x - 90*x^2 + 44*x^3 - 8*x^4 + 0.7*x^5``; the formula's
    interval is ``[0.5, 1.0]``.

    The real root, graphically, by bisection to `es = 10%` and by false position to `es = 0.2%`.
    """

    number = (1, 4, 6, 12)
    name = "Problem 5.3"
    params = ()
    location_in_publication = "Prob. 5.3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.5 \c"),),
        expression=r"-25 + 82 \tmp{u} - 90 \tmp{u}^{2} + 44 \tmp{u}^{3} - 8 \tmp{u}^{4} + 0.7 \tmp{u}^{5}",
        interval="[0.5, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.5 * c
        return -25 + 82 * x - 90 * x**2 + 44 * x**3 - 8 * x**4 + 0.7 * x**5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.65, c=0.0, expected=1.0116703437500003),
        FormulaTestCase.value(params={}, x=0.65, c=0.25, expected=-0.969146965820312),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.0)),
    )
