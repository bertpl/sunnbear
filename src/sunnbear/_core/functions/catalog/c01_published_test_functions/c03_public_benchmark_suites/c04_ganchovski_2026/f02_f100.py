"""This module holds a formula of Ganchovski (2026).

The formula comes from the row with the key ``f100`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.math_functions import real_root


class Ganchovski2026F100(Formula):
    """This formula comes from Ganchovski (2026).

    The survey writes the source's function as ``cbrt((4*x - 3)/x)``; the formula's interval is ``[0, e]``.

    The root line, `$Root{f_100(x); x ∈ [0; e]}`, is the only `$Root` line in the PDF without `= 0`.

    The value ``e`` is rounded to 12 significant digits, the most that a parameter value holds.

    With ``modified = 1``, the interval starts at ``0.03``, right of 0 by 1% of the published interval's width, rounded
    half up to 1 significant digit; ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new
    interval.

    The published test function fails a benchmark suite's checks of its test functions, because ``f(a)`` divides by 0.
    """

    number = (1, 3, 4, 2)
    name = "f100"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Ganchovski, N. (2026). Root-finding Test Functions. The file `Test functions.pdf` in the "
            "repository https://github.com/Proektsoft-EOOD/ModAB-Root-Finding at commit "
            "`b3309e9a5177d6305ac84deba6537adb9b878c5e`: "
            "https://raw.githubusercontent.com/Proektsoft-EOOD/ModAB-Root-Finding/b3309e9a5177d6305ac84deba6537adb9b878c5e/Test%20functions.pdf."
            "\n"
            "- The PDF prints no author or date: its metadata give 2026-09-29 as its creation date. The"
            " repository's README puts it under the MIT License of `C/LICENSE`, which names Ned "
            "Ganchovski as the copyright holder.\n"
            '- An earlier version was posted on ResearchGate in 2023 as "Additional test functions", '
            "https://www.researchgate.net/publication/373922895_Additional_test_functions; "
            "roots-fortran (`roots_fortran`) cites that version."
        ),
        location="f100",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return real_root((4 * x - 3) / x, 3)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.0, 2.71828182846, 2.72, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.03, 2.71828182846, 2.69, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 2.71828182846, "c_scale": 2.72, "modified": 0.0},
            x=0.815485,
            c=0.0,
            expected=0.6848497192199624,
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 2.71828182846, "c_scale": 2.72, "modified": 0.0},
            x=0.815485,
            c=0.25,
            expected=-2.62764740296579,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 2.71828182846, "c_scale": 2.72, "modified": 0.0}, expected=(0.0, 2.71828182846)
        ),
        FormulaTestCase.value(
            params={"a": 0.03, "b": 2.71828182846, "c_scale": 2.69, "modified": 1.0},
            x=0.836485,
            c=0.25,
            expected=-2.4269166802380413,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.03, "b": 2.71828182846, "c_scale": 2.69, "modified": 1.0}, expected=(0.03, 2.71828182846)
        ),
    )
