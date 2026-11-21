"""This module holds a formula of Ganchovski (2026).

The formula comes from the row with the key ``f100`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import real_root


class Ganchovski2026F100(Formula):
    """This formula comes from Ganchovski (2026).

    The survey writes the source's function as ``cbrt((4*x - 3)/x)``; the formula's interval is ``[0, e]``.

    The root line, `$Root{f_100(x); x ∈ [0; e]}`, is the only `$Root` line in the PDF without `= 0`.
    """

    number = (1, 3, 4, 2)
    name = "f100"
    params = ()
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
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2.72 \c"),),
        expression=r"\sqrt[3]{\frac{4 \tmp{u} - 3}{\tmp{u}}}",
        interval="[0, e]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.72 * c
        return real_root((4 * x - 3) / x, 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.718281828459045)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.815485, c=0.0, expected=0.6848497192199624),
        FormulaTestCase.value(params={}, x=0.815485, c=0.25, expected=-2.62764740296579),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.718281828459045)),
    )
