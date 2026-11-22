"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``19`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy2026Problem19(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``(x - 1)^3 + 4*(x - 1)^2 - 10``; the formula's interval is ``[0, 3]``.
    """

    number = (1, 2, 18, 4)
    name = "Problem 19"
    params = ()
    location_in_publication = "dataset.json, problem 19"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\left(\tmp{u} - 1\right)^{3} + 4 \left(\tmp{u} - 1\right)^{2} - 10",
        interval="[0, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return (x - 1) ** 3 + 4 * (x - 1) ** 2 - 10

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.0, expected=-9.961),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-7.724125),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
