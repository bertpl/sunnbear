"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f27`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import sign


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF27(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(81 - p(x)*(108 - p(x)*(54 - p(x)*(12 - p(x)))))*sign(p(x) - 3)``,
    where ``p(x) = x + 1.11111``; the formula's interval is ``[1, 3]``.

    ``Test Functions.pdf`` prints ``p(x) = x + 1.11``.
    """

    number = (1, 1, 13, 4)
    name = "Function f27"
    params = ()
    location_in_publication = "Table 2, f27"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - 2 \c"),
            (r"\tmp{p}", r"\tmp{u} + 1.11111"),
        ),
        expression=r"(81 - \tmp{p}(108 - \tmp{p}(54 - \tmp{p}(12 - \tmp{p})))) \operatorname{sgn}(\tmp{p} - 3)",
        interval="[1, 3]",
        summary=(
            r"A 4th power in Horner form, times a sign so that it changes sign at its root; rounding errors decide its "
            r"sign within about $5 \cdot 10^{-4}$ of that root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        p = x + 1.11111
        return (81 - p * (108 - p * (54 - p * (12 - p)))) * sign(p - 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.6, c=0.0, expected=-0.006965142972726102),
        FormulaTestCase.value(params={}, x=1.6, c=0.25, expected=-0.38731632624146395),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
    )
