"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``Fig. 3.8`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Epperson2013Figure38(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``(1/2)*x^2 - 1/2``; the formula's interval is `[0, 4]` (Fig. 3.8).

    Figure only: 2 Newton steps.
    """

    number = (1, 4, 5, 13)
    name = "Figure 3.8"
    params = ()
    location_in_publication = "Fig. 3.8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\frac{\tmp{u}^{2}}{2} - \frac{1}{2}",
        interval="[0, 4]",
        summary="A parabola whose 1 simple root on the interval lies at a distance of 1 above the parabola's vertex.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return (1 / 2) * x**2 - 1 / 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.2, c=0.0, expected=0.21999999999999995),
        FormulaTestCase.value(params={}, x=1.2, c=0.1, expected=-0.48),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 4.0)),
    )
