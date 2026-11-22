"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``36`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Ellithy202636(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``(x - 1.8)^6 * (x - 1.81)``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 2, 18, 19)
    name = "36"
    params = ()
    location_in_publication = "dataset.json, problem 36"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\left(\tmp{u} - 1.8\right)^{6} \left(\tmp{u} - 1.81\right)",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x - 1.8) ** 6 * (x - 1.81)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-3.6130406400000004),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-41.27524299),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
