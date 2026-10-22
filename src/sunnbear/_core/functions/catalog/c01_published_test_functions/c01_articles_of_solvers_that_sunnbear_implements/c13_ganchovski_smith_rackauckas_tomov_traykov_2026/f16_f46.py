"""This module holds the formula of f46 in Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2026_ganchovski_et_al`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "506d9303d26ba5d7"


class GanchovskiSmithRackauckasTomovTraykov2026F46(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``(exp(-5*x) - x - 0.5)/x^5``; the formula's interval is ``[0.09, 0.7]``.
    """

    number = (1, 1, 13, 16)
    name = "f46"
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
        location="f46",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 0.61 * c
        return (math.exp(-5 * x) - x - 0.5) / x**5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.09, 0.7)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=0.273, c=0.0, expected=-341.3479083845647),
        FormulaTestCase.value(params={}, x=0.273, c=0.25, expected=-2875.6536869539377),
        FormulaTestCase.interval_bounds(params={}, expected=(0.09, 0.7)),
    )
