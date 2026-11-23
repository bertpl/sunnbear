"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.4`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem54(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``-12 - 21*x + 18*x^2 - 2.75*x^3``; the formula's interval is ``[-1,
    0]``.

    The roots graphically; the first root by bisection and false position to `es = 1%`.
    """

    number = (1, 4, 6, 13)
    name = "Problem 5.4"
    params = ()
    location_in_publication = "Prob. 5.4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"-12 - 21 \tmp{u} + 18 \tmp{u}^{2} - 2.75 \tmp{u}^{3}",
        interval="[-1, 0]",
        summary="A cubic with 3 real roots, decreasing and convex on the interval, which holds only the lowest root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return -12 - 21 * x + 18 * x**2 - 2.75 * x**3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.7, c=0.0, expected=12.463249999999999),
        FormulaTestCase.value(params={}, x=-0.7, c=0.25, expected=26.55278125),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 0.0)),
    )
