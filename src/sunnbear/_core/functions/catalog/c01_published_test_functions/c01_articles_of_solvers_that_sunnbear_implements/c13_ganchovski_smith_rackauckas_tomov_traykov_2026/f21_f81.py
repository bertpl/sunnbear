"""This module holds the formula of f81 in Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2026_ganchovski_et_al`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "6181efee459707a3"


class GanchovskiSmithRackauckasTomovTraykov2026F81(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``if(x > -1; 1 + sin(1/(x + 1)); -1)``; the formula's interval is ``[-1, 1]``.

    TF prints the first branch as `1 + sin(1/(x + 1)) - 1` and the second as `0`. TF draws the closing brace of a case
    brace only where a term follows it (f35, f76), and draws none here, so the `- 1` belongs to the first branch and the
    else branch is 0. TF's root, -0.682, is a zero of that first branch, `sin(1/(x + 1))`.
    """

    number = (1, 1, 13, 21)
    name = "f81"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Just-A-Random-Geek/ModAB-Root-Finding."
        ),
        location="f81",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 2.0 * c
        return (1 + math.sin(1 / (x + 1))) if (x) > (-1) else (-1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=1.995407957751765),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=0.45597888911062834),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
