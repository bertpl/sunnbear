"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``§2.8 case (3); P34(iii)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Atkinson1989Case3(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``-1 + x*(3 + x*(-3 + x))``; the formula's interval is ``[0, 3]``.

    Triple root 1: Brent's algorithm takes 50 iterations to reach 1.000001, where bisection would take 19.
    """

    number = (1, 4, 1, 6)
    name = "Case (3)"
    params = ()
    location_in_publication = "§2.8 case (3); Problem 34(iii)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"-1 + \tmp{u} \left(3 + \tmp{u} \left(-3 + \tmp{u}\right)\right)",
        interval="[0, 3]",
        summary=(
            r"$(\tmp{u} - 1)^3$ evaluated in Horner form, with computed values of 0 or of either sign within about $7 "
            r"\cdot 10^{-6}$ of the triple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return -1 + x * (3 + x * (-3 + x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.0, expected=-0.0009999999999999994),
        FormulaTestCase.value(params={}, x=0.9, c=0.75, expected=-0.6141249999999999),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
