"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f87`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026F87(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``1/(x - 0.5) - 2 - 0.05``; the formula's interval is ``[0.6, 2.0]``.
    """

    number = (1, 1, 13, 25)
    name = "f87"
    params = ()
    location_in_publication = "Table 2, f87"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.4 \c"),),
        expression=r"\frac{1}{\tmp{u} - 0.5} - 2 - 0.05",
        interval="[0.6, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.4 * c
        return 1 / (x - 0.5) - 2 - 0.05

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.6, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.02, c=0.0, expected=-0.126923076923077),
        FormulaTestCase.value(params={}, x=1.02, c=0.25, expected=3.8323529411764694),
        FormulaTestCase.interval_bounds(params={}, expected=(0.6, 2.0)),
    )
