"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem52(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``5*x^3 - 5*x^2 + 6*x - 2``; the formula's interval is ``[0, 1]``.

    The real root, graphically and by bisection to `es = 10%`.
    """

    number = (1, 4, 6, 11)
    name = "Problem 5.2"
    params = ()
    location_in_publication = "Prob. 5.2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"5 \tmp{u}^{3} - 5 \tmp{u}^{2} + 6 \tmp{u} - 2",
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 5 * x**3 - 5 * x**2 + 6 * x - 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.515),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-1.711875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
