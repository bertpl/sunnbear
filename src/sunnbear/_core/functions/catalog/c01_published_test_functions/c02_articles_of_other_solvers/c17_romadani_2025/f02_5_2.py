"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.2`` in the survey of published test problems. A script generates this
module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/` and
run `uv run python -m scripts.literature_test_problems.formula_modules 2025_romadani_python_implementations`; do not
edit this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "802288c98a34ccd6"


class Romadani202552(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``sin(x) - cos(2*x)^3``; the formula's interval is `[2.5, 3]` (the
    bracketing methods); the search for the exact roots runs over [0, 3].

    The article prints `cos(2*x)^3` as `cos^3(2x)`. Its stated roots are `2.758392986844`, in the bracket, and
    `0.383199666746`, which the fixed-point, Aitken and Steffensen methods reach. The function does not change sign on
    `[0, 3]`, which holds both roots.
    """

    number = (1, 2, 17, 2)
    name = "5.2"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Romadani, M. N. H. (2025). From Theory to Code: Transforming Classical Root-Finding "
            "Methods into Efficient Python Implementations. ICCK Journal of Applied Mathematics 1(3), "
            "154–189. https://doi.org/10.62762/jam.2025.840767."
        ),
        location="5.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 0.5 * c
        return math.sin(x) - math.cos(2 * x) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.5, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=2.65, c=0.0, expected=0.3016541750571082),
        FormulaTestCase.value(params={}, x=2.65, c=0.25, expected=0.5419169962034848),
        FormulaTestCase.interval_bounds(params={}, expected=(2.5, 3.0)),
    )
