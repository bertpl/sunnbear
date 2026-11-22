"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Prob51(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``-0.5*x^2 + 2.5*x + 4.5``; the formula's interval is ``[5, 10]``.

    The real roots, graphically and by the quadratic formula; 3 bisection iterations for the highest root.
    """

    number = (1, 4, 6, 10)
    name = "Prob. 5.1"
    params = ()
    location_in_publication = "Prob. 5.1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"- 0.5 \tmp{u}^{2} + 2.5 \tmp{u} + 4.5",
        interval="[5, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return -0.5 * x**2 + 2.5 * x + 4.5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (5.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=6.5, c=0.0, expected=-0.375),
        FormulaTestCase.value(params={}, x=6.5, c=0.25, expected=3.84375),
        FormulaTestCase.interval_bounds(params={}, expected=(5.0, 10.0)),
    )
