"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f92`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF92(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``x^3 - 0.001``; the formula's interval is ``[-10, 10]``.

    `Test Functions.pdf` names it Nearly asymmetric function; the C# code names it Near symmetric function, and §4.2 of
    the article calls it a nearly symmetrical function. §4.2 also solves it on `[-10, 10]` and plots it in Figure 2, and
    Table 1 gives the iterations at which the original and the proposed modAB switch modes and stop. `Test
    Functions.pdf` writes the interval in its root line as `[-0;10]`; its plot spans `[-10, 10]`.
    """

    number = (1, 1, 13, 30)
    name = "Function f92"
    params = ()
    location_in_publication = "Table 2, f92"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=r"\tmp{u}^{3} - 0.001",
        interval="[-10, 10]",
        summary=r"A cube minus 0.001, nearly flat on a band around $\x = 20 \c$ that ends at the root.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return x**3 - 0.001

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=-64.001),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=-729.001),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
