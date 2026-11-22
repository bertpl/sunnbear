"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-2(e)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Exercise312E(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``3 - 2^x``; the formula's interval is ``[0, 2]``.

    3.1-2 asks for the root to an accuracy of 0.1 by bisection, by hand.
    """

    number = (1, 4, 5, 5)
    name = "Exercise 3.1-2(e)"
    params = ()
    location_in_publication = "Exercise 3.1-2(e)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"3 - 2^{\tmp{u}}",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return 3 - 2**x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=1.484283433489602),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=1.9282265374637069),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
