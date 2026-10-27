"""This module holds formula f1.99.1.13.21, the modified version of the published formula f1.1.13.21.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.13.21 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedGanchovskiSmithRackauckasTomovTraykov2026F81(Formula):
    """This formula is the modified version of formula f1.1.13.21, from Ganchovski et al. (2026).

    The survey writes the source's function as ``if(x > -1; 1 + sin(1/(x + 1)); -1)``; the published interval is
    ``[-1, 1]``.

    `Test Functions.pdf` prints the first branch as `1 + sin(1/(x + 1)) - 1` and the second as `0`, with no closing
    brace after the case brace. That layout is a misprint of `if(x > -1; 1 + sin(1/(x + 1)); 0) - 1`, Oliveira &
    Takahashi's function, which the authors' Calcpad worksheet `Root finding tests.cpd` defines (commit `0d6efd5` of
    https://github.com/Just-A-Random-Geek/ModAB-Root-Finding); as printed, the function is 0 at the left end `x = -1`,
    where a bracketing method on `[-1, 1]` stops in place of the printed root -0.682.

    The formula's interval starts at ``-1.02``, left of the jump at -1 by 1% of the published interval's width, rounded
    half up to 1 significant digit; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the
    new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the jump lies at
    ``a = -1``: with any ``c < 0``, ``f(a)`` takes the branch ``1 + sin(1/(x + 1))``, which is never negative, so that
    ``f`` no longer changes sign on the interval.
    """

    number = (1, 99, 1, 13, 21)
    name = "f81"
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
        location="f81",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.02 * c
        if x > -1:
            return 1 + math.sin(1 / (x + 1))
        else:
            return -1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.02, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.414, c=0.25, expected=0.7810954965230892),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.02, 1.0)),
        FormulaTestCase.value(params={}, x=-1.01, c=0.0, expected=-1.0),
    )
