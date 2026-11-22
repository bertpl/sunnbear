"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f45`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026F45(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``x^7``; the formula's interval is ``[-1, 1.5]``.
    """

    number = (1, 1, 13, 15)
    name = "f45"
    params = ()
    location_in_publication = "Table 2, f45"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.5 \c"),),
        expression=r"\tmp{u}^{7}",
        interval="[-1, 1.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.5 * c
        return x**7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.25, c=0.0, expected=-6.103515625e-05),
        FormulaTestCase.value(params={}, x=-0.25, c=0.25, expected=-0.39269590377807617),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.5)),
    )
