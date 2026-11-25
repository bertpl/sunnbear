"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-12; 2.2-7; 2.4-6; 2.5-8`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Bradie2006Exercise2112(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``1/x - 37``; the formula's interval is `(0.01, 0.1)` (2.2-7, 2.4-6,
    2.5-8).

    Root `1/37`. 2.1-12 asks for 5 decimal places by bisection, with no interval.
    """

    number = (1, 4, 4, 17)
    name = "Exercise 2.1-12"
    params = ()
    location_in_publication = "Exercises 2.1-12, 2.2-7, 2.4-6, 2.5-8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.1 \c"),),
        expression=r"\frac{1}{\tmp{u}} - 37",
        interval="[0.01, 0.1]",
        summary=(
            r"A hyperbola with 1 simple root on the interval and a pole at $\x = 0.1 \c$, just below the lower bound."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.1 * c
        return 1 / x - 37

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.037, c=0.0, expected=-9.972972972972972),
        FormulaTestCase.value(params={}, x=0.037, c=0.225, expected=31.965517241379317),
        FormulaTestCase.interval_bounds(params={}, expected=(0.01, 0.1)),
    )
