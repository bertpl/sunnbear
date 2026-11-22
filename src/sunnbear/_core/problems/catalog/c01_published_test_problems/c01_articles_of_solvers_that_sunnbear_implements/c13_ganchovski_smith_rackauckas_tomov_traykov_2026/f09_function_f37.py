"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f37`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF37(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(x - 7/9)^3 + (x - 7/9)*10^-3``; the formula's interval is ``[-11,
    9]``.
    """

    number = (1, 1, 13, 9)
    name = "Function f37"
    params = ()
    location_in_publication = "Table 2, f37"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\left(\tmp{u} - \frac{7}{9}\right)^{3} + \frac{\tmp{u} - \frac{7}{9}}{10^{3}}",
        interval="[-11, 9]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return (x - 7 / 9) ** 3 + (x - 7 / 9) * 10**-3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-11.0, 9.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-5.0, c=0.0, expected=-192.8836927297668),
        FormulaTestCase.value(params={}, x=-5.0, c=0.25, expected=-1251.9627668038409),
        FormulaTestCase.interval_bounds(params={}, expected=(-11.0, 9.0)),
    )
