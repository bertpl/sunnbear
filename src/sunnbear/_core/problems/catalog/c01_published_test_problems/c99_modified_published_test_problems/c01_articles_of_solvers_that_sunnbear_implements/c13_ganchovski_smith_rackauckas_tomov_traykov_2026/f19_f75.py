"""This module holds formula f1.99.1.13.19, the modified version of the published formula f1.1.13.19.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.13.19 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import sign


class ModifiedGanchovskiSmithRackauckasTomovTraykov2026F75(Formula):
    """This formula is the modified version of formula f1.1.13.19, from Ganchovski et al. (2026).

    The survey writes the source's function as ``sign(3*x - 1)*(1 - sqrt(1 - (3*x - 1)^2/81))``; the published interval
    is ``[-1, 1]``.

    The formula computes the published function in the equivalent form
    ``sign(3*x - 1) * ((3*x - 1)**2/81) / (1 + sqrt(1 - (3*x - 1)**2/81))``, on the published interval, and ``c`` shifts
    x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``sqrt(1 - (3*x - 1)**2/81)`` rounds to 1, and its subtraction from 1 cancels, so that f is exactly 0
    at many x-values within about 2e-8 of the root; the equivalent form has no subtraction that cancels.
    """

    number = (1, 99, 1, 13, 19)
    name = "f75"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        location="f75",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, in an equivalent form without cancellation.

        The form is ``sign(3*y - 1) * ((3*y - 1)**2/81) / (1 + sqrt(1 - (3*y - 1)**2/81))``. Category 1 states the rule
        for ``c_scale``.
        """
        x = x - 2.0 * c
        return sign(3 * x - 1) * ((3 * x - 1) ** 2 / 81) / (1 + math.sqrt(1 - (3 * x - 1) ** 2 / 81))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.08841475751250358),
    )
