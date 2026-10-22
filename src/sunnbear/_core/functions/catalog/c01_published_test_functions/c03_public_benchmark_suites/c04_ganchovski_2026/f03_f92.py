"""This module holds a formula of Ganchovski (2026).

The formula comes from the row with the key ``f92`` in the survey of published test problems. A script generates this
module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/` and
run `uv run python -m scripts.literature_test_problems.formula_modules ganchovski_test_functions`; do not edit this
file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "6b1ffecbdf32f4d1"


class Ganchovski2026F92(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``x^3 - 0.001``; the formula's intervals are `[-0, 10]`; `[-10, 10]`
    (plot, p. 16).

    As the root line prints it; the plot spans `[-10, 10]`.
    """

    number = (1, 3, 4, 3)
    name = "f92"
    param_names = ("a", "b")
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
        location="f92",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return x**3 - 0.001

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b"), rows=((0.0, 10.0), (-10.0, 10.0))),)

    cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 10.0}, x=3.0, c=0.0, expected=26.999),
        FormulaTestCase.value(params={"a": 0.0, "b": 10.0}, x=3.0, c=0.25, expected=0.124),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0}, x=-4.0, c=0.0, expected=-64.001),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 10.0}, expected=(0.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0}, expected=(-10.0, 10.0)),
    )
