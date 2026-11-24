"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f90`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF90(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``x^3 - 2*x^2 + x - 0.025``; the formula's interval is ``[-1.0, 2.0]``.
    """

    number = (1, 1, 13, 28)
    name = "Function f90"
    params = ()
    location_in_publication = "Table 2, f90"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\tmp{u}^{3} - 2 \tmp{u}^{2} + \tmp{u} - 0.025",
        interval="[-1, 2]",
        summary=(
            r"$\tmp{u} (\tmp{u} - 1)^2$ lowered by 0.025, which splits its double root into 2 simple roots 0.32 apart, "
            r"with a third root near $\x = 3 \c$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x**3 - 2 * x**2 + x - 0.025

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.1, c=0.0, expected=-0.14600000000000002),
        FormulaTestCase.value(params={}, x=-0.1, c=0.25, expected=-2.934125),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 2.0)),
    )
