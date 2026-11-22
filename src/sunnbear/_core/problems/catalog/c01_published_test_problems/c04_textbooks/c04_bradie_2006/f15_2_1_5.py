"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006215(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^6 - 3``; the formula's interval is ``(1, 2)``.

    Root `3^(1/6)`; as 2.1-4.
    """

    number = (1, 4, 4, 15)
    name = "2.1-5"
    params = ()
    location_in_publication = "Exercise 2.1-5"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{6} - 3",
        interval="[1, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**6 - 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=1.826809000000001),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-1.6599043593749996),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
