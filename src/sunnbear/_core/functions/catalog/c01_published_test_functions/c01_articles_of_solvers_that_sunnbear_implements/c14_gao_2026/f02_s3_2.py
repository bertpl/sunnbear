"""This module holds the formula of S3.2 in Gao (2026).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2026_gao`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import real_root

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "6dc0693040b3033f"


class Gao2026S32(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``x^(1/5)/(1 + abs(x)^(1/5))``; the formula's interval is ``[-5, 10]``.

    Printed with 5th-root signs. Results in Table 1.
    """

    number = (1, 1, 14, 2)
    name = "S3.2"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied "
            "Mathematics Letters 178, 109928. https://doi.org/10.1016/j.aml.2026.109928."
        ),
        location="S3.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 15.0 * c
        return real_root(x, 5) / (1 + real_root(abs(x), 5))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-5.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-0.5, c=0.0, expected=-0.4653980386192365),
        FormulaTestCase.value(params={}, x=-0.5, c=0.25, expected=-0.5718452694455244),
        FormulaTestCase.interval_bounds(params={}, expected=(-5.0, 10.0)),
    )
