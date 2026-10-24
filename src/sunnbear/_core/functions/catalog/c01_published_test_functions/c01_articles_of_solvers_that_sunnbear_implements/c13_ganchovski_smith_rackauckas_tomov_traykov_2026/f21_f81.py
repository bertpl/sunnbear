"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f81`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class GanchovskiSmithRackauckasTomovTraykov2026F81(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``if(x > -1; 1 + sin(1/(x + 1)); -1)``; the formula's interval is ``[-1,
    1]``.

    `Test Functions.pdf` prints the first branch as `1 + sin(1/(x + 1)) - 1` and the second as `0`, with no closing
    brace after the case brace. That layout is a misprint of `if(x > -1; 1 + sin(1/(x + 1)); 0) - 1`, Oliveira &
    Takahashi's function, which the authors' Calcpad worksheet `Root finding tests.cpd` defines (commit `0d6efd5` of
    https://github.com/Just-A-Random-Geek/ModAB-Root-Finding); as printed, the function is 0 at the left end `x = -1`,
    where a bracketing method on `[-1, 1]` stops in place of the printed root -0.682.

    With ``modified = 1``, the interval starts at ``-1.02``, left of the jump at -1 by 1% of the published interval's
    width, rounded half up to 1 significant digit; ``c`` shifts x as category 1 states, with the ``c_scale`` of the new
    interval.

    The published test function fails a benchmark suite's checks of its test functions, because ``a = -1`` sits on the
    jump: a shift along x by any ``c < 0`` evaluates at ``a`` the expression ``1 + sin(1/(x + 1))``, which is never
    negative, so that ``f`` no longer changes sign on the interval.
    """

    number = (1, 1, 13, 21)
    name = "f81"
    param_names = ("a", "b", "c_scale", "modified")
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
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if x > -1:
            return 1 + math.sin(1 / (x + 1))
        else:
            return -1

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-1.0, 1.0, 2.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-1.02, 1.0, 2.02, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 0.0}, x=-0.4, c=0.0, expected=1.995407957751765
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 0.0}, x=-0.4, c=0.25, expected=0.45597888911062834
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 0.0}, x=-1.0, c=0.0, expected=-1.0
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 0.0}, expected=(-1.0, 1.0)
        ),
        FormulaTestCase.value(
            params={"a": -1.02, "b": 1.0, "c_scale": 2.02, "modified": 1.0},
            x=-0.414,
            c=0.25,
            expected=0.7810954965230892,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.02, "b": 1.0, "c_scale": 2.02, "modified": 1.0}, expected=(-1.02, 1.0)
        ),
    )
