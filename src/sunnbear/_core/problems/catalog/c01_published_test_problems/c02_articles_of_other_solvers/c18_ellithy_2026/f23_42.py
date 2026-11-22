"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``42`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy202642(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^6 - 8*x^5 + 24*x^4 - 32*x^3 + 16*x^2``; the formula's interval is
    ``[0, 4]``.
    """

    number = (1, 2, 18, 23)
    name = "42"
    params = ()
    location_in_publication = "dataset.json, problem 42"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"\tmp{u}^{6} - 8 \tmp{u}^{5} + 24 \tmp{u}^{4} - 32 \tmp{u}^{3} + 16 \tmp{u}^{2}",
        interval="[0, 4]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return x**6 - 8 * x**5 + 24 * x**4 - 32 * x**3 + 16 * x**2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.2, c=0.0, expected=0.5898240000000001),
        FormulaTestCase.value(params={}, x=1.2, c=0.25, expected=0.41990399999999983),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 4.0)),
    )
