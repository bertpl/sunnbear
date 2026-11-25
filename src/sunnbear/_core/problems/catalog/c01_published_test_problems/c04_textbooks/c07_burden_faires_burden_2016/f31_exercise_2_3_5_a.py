"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-5(a); 2.6-1(a)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise235A(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - 2*x^2 - 5``; the formula's interval is ``[1, 4]``.

    Newton to `1E-4` (2.3-5); all real zeros by Newton to `1E-4` (2.6-1).
    """

    number = (1, 4, 7, 31)
    name = "Exercise 2.3-5(a)"
    params = ()
    location_in_publication = "Exercises 2.3-5(a), 2.6-1(a)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} - 2 \tmp{u}^{2} - 5",
        interval="[1, 4]",
        summary="A cubic with only 1 real root and a shallow local minimum 1.36 below that root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - 2 * x**2 - 5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.9, c=0.0, expected=-5.361000000000001),
        FormulaTestCase.value(params={}, x=1.9, c=0.75, expected=-6.124125),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 4.0)),
    )
