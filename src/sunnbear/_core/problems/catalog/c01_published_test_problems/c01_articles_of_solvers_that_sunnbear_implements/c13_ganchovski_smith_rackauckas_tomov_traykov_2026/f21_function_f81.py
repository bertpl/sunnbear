"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f81`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF81(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``if(x > -1; 1 + sin(1/(x + 1)); -1)``; the formula's interval is ``[-1,
    1]``.

    `Test Functions.pdf` prints the first branch as `1 + sin(1/(x + 1)) - 1` and the second as `0`, with no closing
    brace after the case brace. That layout is a misprint of `if(x > -1; 1 + sin(1/(x + 1)); 0) - 1`, Oliveira &
    Takahashi's function, which the authors' Calcpad worksheet `Root finding tests.cpd` defines (commit `0d6efd5` of
    https://github.com/Just-A-Random-Geek/ModAB-Root-Finding); as printed, the function is 0 at the left end `x = -1`,
    where a bracketing method on `[-1, 1]` stops in place of the printed root -0.682.
    """

    number = (1, 1, 13, 21)
    name = "Function f81"
    params = ()
    location_in_publication = "Table 2, f81"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\begin{cases} 1 + \sin{\left(\frac{1}{\tmp{u} + 1} \right)} & \text{for}\: \tmp{u} > -1 "
            r"\\-1 & \text{otherwise} \end{cases}"
        ),
        interval="[-1, 1]",
        summary=(
            r"A function negative only up to $\x = \c - 1$ and, above that point, oscillating ever faster toward it "
            r'and touching 0 infinitely often, referred to in the source as "Warsaw".'
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        if x > -1:
            return 1 + math.sin(1 / (x + 1))
        else:
            return -1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=1.995407957751765),
        FormulaTestCase.value(params={}, x=-0.4, c=0.5, expected=0.45597888911062834),
        FormulaTestCase.value(params={}, x=-1.0, c=0.0, expected=-1.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
