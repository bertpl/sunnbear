"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-18`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise2118(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 + x - 4``; the formula's interval is ``[1, 4]``.

    As 2.1-17, to `1E-3`.
    """

    number = (1, 4, 7, 25)
    name = "Exercise 2.1-18"
    params = ()
    location_in_publication = "Exercise 2.1-18"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} + \tmp{u} - 4",
        interval="[1, 4]",
        summary="An increasing cubic with 1 real root and a slope of at least 1 everywhere.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 + x - 4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.9, c=0.0, expected=4.758999999999999),
        FormulaTestCase.value(params={}, x=1.9, c=0.75, expected=-1.3291250000000003),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 4.0)),
    )
