"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``33`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy202633(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^4 - 10*x^3 + 35*x^2 - 50*x + 24``; the formula's interval is ``[0,
    1.5]``.
    """

    number = (1, 2, 18, 16)
    name = "33"
    params = ()
    location_in_publication = "dataset.json, problem 33"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.5 \c"),),
        expression=r"\tmp{u}^{4} - 10 \tmp{u}^{3} + 35 \tmp{u}^{2} - 50 \tmp{u} + 24",
        interval="[0, 1.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return x**4 - 10 * x**3 + 35 * x**2 - 50 * x + 24

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=7.71725625),
        FormulaTestCase.value(params={}, x=0.45, c=0.25, expected=20.442687890625),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
