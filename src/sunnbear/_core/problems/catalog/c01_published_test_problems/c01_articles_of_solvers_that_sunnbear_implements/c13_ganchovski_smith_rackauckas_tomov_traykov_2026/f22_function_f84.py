"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f84`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF84(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(x - 1)*(x - 2)*(x - 3)*(x - 4)*(x - 5) - 0.05``; the formula's
    interval is ``[0.5, 5.5]``.
    """

    number = (1, 1, 13, 22)
    name = "Function f84"
    params = ()
    location_in_publication = "Table 2, f84"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=(
            r"\left(\tmp{u} - 1\right) \left(\tmp{u} - 2\right) \left(\tmp{u} - 3\right) \left(\tmp{u} -"
            r" 4\right) \left(\tmp{u} - 5\right) - 0.05"
        ),
        interval="[0.5, 5.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return (x - 1) * (x - 2) * (x - 3) * (x - 4) * (x - 5) - 0.05

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 5.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.0, c=0.0, expected=-0.05),
        FormulaTestCase.value(params={}, x=2.0, c=0.25, expected=-9.7619140625),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 5.5)),
    )
