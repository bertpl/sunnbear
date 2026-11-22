"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f40`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF40(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``if(x = 0; 0.0; 1/(x - 2/3))``; the formula's interval is ``[-11, 9]``.
    """

    number = (1, 1, 13, 11)
    name = "Function f40"
    params = ()
    location_in_publication = "Table 2, f40"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=(
            r"\begin{cases} 0.0 & \text{for}\: \tmp{u} = 0 \\\frac{1}{\tmp{u} - \frac{2}{3}} & "
            r"\text{otherwise} \end{cases}"
        ),
        interval="[-11, 9]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        if x == 0:
            return 0.0
        else:
            return 1 / (x - 2 / 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-11.0, 9.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-5.0, c=0.0, expected=-0.17647058823529413),
        FormulaTestCase.value(params={}, x=-5.0, c=0.25, expected=-0.09375),
        FormulaTestCase.value(params={}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-11.0, 9.0)),
    )
