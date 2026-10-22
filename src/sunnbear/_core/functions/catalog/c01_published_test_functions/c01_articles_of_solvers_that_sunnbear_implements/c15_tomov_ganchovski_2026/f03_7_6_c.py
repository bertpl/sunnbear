"""This module holds the formula of 7.6-c in Tomov, Ganchovski (2026).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2026_tomov_ganchovski`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "b76f00a165e264b8"


class TomovGanchovski202676C(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``x``; the formula's interval is ``[-1, 1]``.

    The evaluation at the midpoint is replaced by NaN; the solver must report invalid input.
    """

    number = (1, 1, 15, 3)
    name = "7.6-c"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Tomov, L., Ganchovski, N. (2026). Global convergence and reliable stopping in a "
            "safeguarded modified Anderson–Björck method. arXiv preprint 2610.14193. "
            "https://doi.org/10.48550/arxiv.2610.14193 (https://arxiv.org/abs/2610.14193). The authors'"
            " C# code and benchmark definitions are in "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding; Section 7.3 pins commit "
            "`9111cdcc6912401eb684a7b771df3a469795d5b8` (the preprint's reference [16]), and Section "
            "7.4 pins commit `51a6d1b` (reference [17])."
        ),
        location="7.6-c",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        return x - 2.0 * c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.9),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
