"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.8`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem58(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``x^2 - 18``; the formula's interval is ``[4, 5]``.

    The problem asks for the positive square root of 18 by false position to `es = 0.5%`; it prints no function.
    """

    number = (1, 4, 6, 17)
    name = "Problem 5.8"
    params = ()
    location_in_publication = "Prob. 5.8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} - 18",
        interval="[4, 5]",
        summary="A parabola, increasing and close to a line on the interval, with 1 simple root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - 18

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.3, c=0.0, expected=0.4899999999999985),
        FormulaTestCase.value(params={}, x=4.3, c=0.25, expected=-1.5975000000000015),
        FormulaTestCase.interval_bounds(params={}, expected=(4.0, 5.0)),
    )
