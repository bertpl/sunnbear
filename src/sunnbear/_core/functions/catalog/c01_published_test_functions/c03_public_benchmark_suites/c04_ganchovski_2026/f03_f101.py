"""This module holds a formula of Ganchovski (2026).

The formula comes from the row with the key ``f101`` in the survey of published test problems. A script generates this
module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/` and
run `uv run python -m scripts.literature_test_problems.formula_modules ganchovski_test_functions`; do not edit this
file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "249b40265ed3335b"


class Ganchovski2026F101(Formula):
    """This formula comes from Ganchovski (2026).

    The survey writes the source's function as ``if(x < 0; -(x^2); 7*x^2)``; the formula's interval is ``[-3, 1]``.

    The root line uses `$Find`.
    """

    number = (1, 3, 4, 3)
    name = "f101"
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
        location="f101",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        if x < 0:
            return -(x**2)
        else:
            return 7 * x**2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.8, c=0.0, expected=-3.24),
        FormulaTestCase.value(params={}, x=-1.8, c=0.25, expected=-7.839999999999999),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=7.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 1.0)),
    )
