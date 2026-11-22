"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``23`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem23(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``-0.9*x^2 + 1.7*x + 2.5``; the formula's interval is ``[2.8, 3.0]``.
    """

    number = (1, 2, 18, 8)
    name = "Problem 23"
    params = ()
    location_in_publication = "dataset.json, problem 23"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.2 \c"),),
        expression=r"- 0.9 \tmp{u}^{2} + 1.7 \tmp{u} + 2.5",
        interval="[2.8, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.2 * c
        return -0.9 * x**2 + 1.7 * x + 2.5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.8, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.86, c=0.0, expected=0.0003600000000004287),
        FormulaTestCase.value(params={}, x=2.86, c=0.25, expected=0.17050999999999983),
        FormulaTestCase.interval_bounds(params={}, expected=(2.8, 3.0)),
    )
