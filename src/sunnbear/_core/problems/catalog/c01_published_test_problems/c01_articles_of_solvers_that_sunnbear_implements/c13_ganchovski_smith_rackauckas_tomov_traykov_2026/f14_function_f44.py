"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f44`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF44(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``x^5``; the formula's interval is ``[-1, 1.5]``.
    """

    number = (1, 1, 13, 14)
    name = "Function f44"
    params = ()
    location_in_publication = "Table 2, f44"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.5 \c"),),
        expression=r"\tmp{u}^{5}",
        interval="[-1, 1.5]",
        summary="A 5th power with a root of multiplicity 5, below $10^{-3}$ in magnitude within 0.25 of it.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.5 * c
        return x**5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.25, c=0.0, expected=-0.0009765625),
        FormulaTestCase.value(params={}, x=-0.25, c=0.25, expected=-0.512908935546875),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.5)),
    )
