"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``21`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem21(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``(x^2 - 4)*(x + 1.5)*(x - 0.5)``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 2, 18, 6)
    name = "Problem 21"
    params = ()
    location_in_publication = "dataset.json, problem 21"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\left(\tmp{u}^{2} - 4\right) \left(\tmp{u} + 1.5\right) \left(\tmp{u} - 0.5\right)",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x**2 - 4) * (x + 1.5) * (x - 0.5)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.7643999999999999),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=2.5536000000000003),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
