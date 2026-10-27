"""This module holds formula f1.99.3.4.2, the modified version of the published formula f1.3.4.2.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.4.2 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import real_root


class ModifiedGanchovski2026F100(Formula):
    """This formula is the modified version of formula f1.3.4.2, from Ganchovski (2026).

    The survey writes the source's function as ``cbrt((4*x - 3)/x)``; the published interval is ``[0, e]``.

    The root line, `$Root{f_100(x); x ∈ [0; e]}`, is the only `$Root` line in the PDF without `= 0`.

    The formula's interval starts at ``0.03``, right of 0 by 1% of the published interval's width, rounded half up to 1
    significant digit; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` divides by
    0.
    """

    number = (1, 99, 3, 4, 2)
    name = "f100"
    param_names = ()
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
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.69 * c
        return real_root((4 * x - 3) / x, 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.03, 2.718281828459045)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.836485, c=0.25, expected=-2.4269166802380413),
        FormulaTestCase.interval_bounds(params={}, expected=(0.03, 2.718281828459045)),
    )
