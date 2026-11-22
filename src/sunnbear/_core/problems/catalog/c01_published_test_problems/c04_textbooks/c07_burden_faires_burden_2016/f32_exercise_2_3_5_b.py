"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-5(b); 2.6-1(b)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise235B(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 + 3*x^2 - 1``; the formula's interval is ``[-3, -2]``.

    As 2.3-5(a). 2.4-2(b) prints, on the same interval, a function that with 1 misprint corrected is its square.
    """

    number = (1, 4, 7, 32)
    name = "Exercise 2.3-5(b)"
    params = ()
    location_in_publication = "Exercises 2.3-5(b), 2.6-1(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} + 3 \tmp{u}^{2} - 1",
        interval="[-3, -2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 + 3 * x**2 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, -2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-2.7, c=0.0, expected=1.186999999999999),
        FormulaTestCase.value(params={}, x=-2.7, c=0.25, expected=-0.5648750000000015),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, -2.0)),
    )
