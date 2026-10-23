"""This module holds a formula of Ganchovski (2026).

The formula comes from the row with the key ``f27`` in the survey of published test problems. The survey gives this
function as an expression in a helper ``p(x)``, which the same row of the survey defines, not as 1 expression in x,
so a person writes this module: a change of the formula's row in `data/literature_test_problems/sources/` needs a
change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import sign


class Ganchovski2026F27(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``(81 - p(x)*(108 - p(x)*(54 - p(x)*(12 - p(x)))))*(sign(p(x) - 3))``,
    where ``p(x) = x + 1.11``; the formula's interval is ``[1, 3]``.
    """

    number = (1, 3, 4, 1)
    name = "f27"
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
        location="f27",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 2.0 * c
        p = x + 1.11
        return (81 - p * (108 - p * (54 - p * (12 - p)))) * sign(p - 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=1.6, c=0.0, expected=-0.007072809999999991),
        FormulaTestCase.value(params={}, x=1.6, c=0.25, expected=-0.3895008099999998),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
    )
