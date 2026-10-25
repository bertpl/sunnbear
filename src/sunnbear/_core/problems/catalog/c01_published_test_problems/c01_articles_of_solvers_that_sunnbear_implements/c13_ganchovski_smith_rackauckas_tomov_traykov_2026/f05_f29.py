"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f29`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class GanchovskiSmithRackauckasTomovTraykov2026F29(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``exp((x - 3)^5) - 1``; the formula's intervals are `[2.6, 4.6]`; `[2.6,
    3.6]` (`Test Functions.pdf`).

    `Test Functions.pdf` gives the interval `[2.6, 3.6]`.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``expm1((x - 3)**5)``, on
    the published intervals, and ``c`` shifts x as category 1 states.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``exp((x - 3)**5)`` rounds to 1, and the subtraction of 1 cancels, so that f is exactly 0 at many
    x-values within about 7e-4 of the root; ``expm1(u)`` computes ``exp(u) - 1`` without the subtraction.
    """

    number = (1, 1, 13, 5)
    name = "f29"
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
        location="f29",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``expm1((y - 3)**5)``, with ``y = x - c_scale*c``. Category 1 states the
        rule for ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 1:
            return math.expm1((x - 3) ** 5)
        else:
            return math.exp((x - 3) ** 5) - 1

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((2.6, 4.6, 2.0, 0.0), (2.6, 3.6, 1.0, 0.0))),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((2.6, 4.6, 2.0, 1.0), (2.6, 3.6, 1.0, 1.0))),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 2.6, "b": 4.6, "c_scale": 2.0, "modified": 0.0}, x=3.2, c=0.0, expected=0.0003200512054617717
        ),
        FormulaTestCase.value(
            params={"a": 2.6, "b": 4.6, "c_scale": 2.0, "modified": 0.0}, x=3.2, c=0.25, expected=-0.002427049940032372
        ),
        FormulaTestCase.value(
            params={"a": 2.6, "b": 3.6, "c_scale": 1.0, "modified": 0.0}, x=2.9, c=0.0, expected=-9.99995000016671e-06
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 2.6, "b": 4.6, "c_scale": 2.0, "modified": 0.0}, expected=(2.6, 4.6)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 2.6, "b": 3.6, "c_scale": 1.0, "modified": 0.0}, expected=(2.6, 3.6)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 2.6, "b": 4.6, "c_scale": 2.0, "modified": 1.0}, expected=(2.6, 4.6)
        ),
        FormulaTestCase.value(
            params={"a": 2.6, "b": 4.6, "c_scale": 2.0, "modified": 1.0}, x=3.2, c=0.25, expected=-0.002427049940032372
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 2.6, "b": 3.6, "c_scale": 1.0, "modified": 1.0}, expected=(2.6, 3.6)
        ),
        FormulaTestCase.value(
            params={"a": 2.6, "b": 3.6, "c_scale": 1.0, "modified": 1.0}, x=2.9, c=0.25, expected=-0.005238418878905655
        ),
    )
