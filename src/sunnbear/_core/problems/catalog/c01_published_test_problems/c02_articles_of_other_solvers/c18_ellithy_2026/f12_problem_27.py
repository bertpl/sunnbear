"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``27`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem27(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^4 - 2*x^2 - 4``; the formula's interval is ``[1, 3]``.
    """

    number = (1, 2, 18, 12)
    name = "Problem 27"
    params = ()
    location_in_publication = "dataset.json, problem 27"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{4} - 2 \tmp{u}^{2} - 4",
        interval="[1, 3]",
        summary="A quartic with 1 root on the interval, 0.80 above the upper of the quartic's 2 minima of $-5$.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**4 - 2 * x**2 - 4

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.6, c=0.0, expected=-2.566399999999999),
        FormulaTestCase.value(params={}, x=1.6, c=0.5, expected=-4.9559),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
    )
