"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f75`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import sign


class GanchovskiSmithRackauckasTomovTraykov2026F75(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``sign(3*x - 1)*(1 - sqrt(1 - (3*x - 1)^2/81))``; the formula's interval
    is ``[-1, 1]``.
    """

    number = (1, 1, 13, 19)
    name = "f75"
    params = ()
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        location="Table 2, f75",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\operatorname{sign}{\left(3 \tmp{u} - 1 \right)} \left(1 - \sqrt{1 - \frac{\left(3 \tmp{u}"
            r" - 1\right)^{2}}{81}}\right)"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return sign(3 * x - 1) * (1 - math.sqrt(1 - (3 * x - 1) ** 2 / 81))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.030336700921269832),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.08841475751250358),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
