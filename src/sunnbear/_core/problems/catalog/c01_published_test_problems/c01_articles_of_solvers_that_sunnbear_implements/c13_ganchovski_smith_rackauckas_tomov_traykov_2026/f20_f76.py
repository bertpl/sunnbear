"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f76`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026F76(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``if(x > (1 - 10^6)/10^6; (1 + 10^6)/10^6; -1)``; the formula's interval
    is ``[-1, 1]``.

    `Test Functions.pdf` prints `if(x > (1 - 10^6)/10^6; (1 + 10^6)/10^6; 0) - 1`, which right of the step is `10^-6`,
    not `1 + 10^-6`.
    """

    number = (1, 1, 13, 20)
    name = "f76"
    params = ()
    location_in_publication = "Table 2, f76"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\begin{cases} \frac{1 + 10^{6}}{10^{6}} & \text{for}\: \tmp{u} > \frac{1 - 10^{6}}{10^{6}}"
            r" \\-1 & \text{otherwise} \end{cases}"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        if x > (1 - 10**6) / 10**6:
            return (1 + 10**6) / 10**6
        else:
            return -1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=1.000001),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=1.000001),
        FormulaTestCase.value(params={}, x=-1.0, c=0.0, expected=-1.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
