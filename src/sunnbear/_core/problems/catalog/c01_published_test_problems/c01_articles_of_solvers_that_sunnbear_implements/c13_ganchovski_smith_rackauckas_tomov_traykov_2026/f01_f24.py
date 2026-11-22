"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f24`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026F24(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(x + 2)*(x + 1)*(x - 3)^3``; the formula's interval is ``[2.6, 4.6]``.
    """

    number = (1, 1, 13, 1)
    name = "f24"
    params = ()
    location_in_publication = "Table 2, f24"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\left(\tmp{u} + 2\right) \left(\tmp{u} + 1\right) \left(\tmp{u} - 3\right)^{3}",
        interval="[2.6, 4.6]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return (x + 2) * (x + 1) * (x - 3) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.6, 4.6)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.2, c=0.0, expected=0.17472000000000049),
        FormulaTestCase.value(params={}, x=3.2, c=0.25, expected=-0.4695299999999992),
        FormulaTestCase.interval_bounds(params={}, expected=(2.6, 4.6)),
    )
