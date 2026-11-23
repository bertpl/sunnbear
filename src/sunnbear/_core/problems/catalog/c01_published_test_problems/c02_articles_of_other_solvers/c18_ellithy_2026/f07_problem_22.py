"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``22`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem22(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^3 - 3*x^2 - 4*x + 13``; the formula's interval is ``[-3, -2]``.
    """

    number = (1, 2, 18, 7)
    name = "Problem 22"
    params = ()
    location_in_publication = "dataset.json, problem 22"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{3} - 3 \tmp{u}^{2} - 4 \tmp{u} + 13",
        interval="[-3, -2]",
        summary="A cubic whose 1 root lies within 0.05 of the upper bound.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - 3 * x**2 - 4 * x + 13

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, -2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-2.7, c=0.0, expected=-17.753000000000007),
        FormulaTestCase.value(params={}, x=-2.7, c=0.25, expected=-26.979875000000007),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, -2.0)),
    )
