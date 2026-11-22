"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``32`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy202632(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^4 + 2*x^2 - x - 1``; the formula's interval is ``[-0.5, 0]``.
    """

    number = (1, 2, 18, 15)
    name = "32"
    params = ()
    location_in_publication = "dataset.json, problem 32"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.5 \c"),),
        expression=r"\tmp{u}^{4} + 2 \tmp{u}^{2} - \tmp{u} - 1",
        interval="[-0.5, 0]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.5 * c
        return x**4 + 2 * x**2 - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.5, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.35, c=0.0, expected=-0.3899937500000001),
        FormulaTestCase.value(params={}, x=-0.35, c=0.25, expected=-0.022843359375000073),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.5, 0.0)),
    )
