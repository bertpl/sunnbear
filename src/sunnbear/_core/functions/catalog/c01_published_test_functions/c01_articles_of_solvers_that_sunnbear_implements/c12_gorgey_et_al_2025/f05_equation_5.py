"""This module holds the formula of Equation 5 in Gorgey et al. (2025).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2025_gorgey`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "3c5783006e2c374c"


class GorgeyEtAl2025Equation5(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``x*sin(x) - x^2*exp(x) + exp(-x) + cos(x)``; the formula's interval is ``[-1, 1]``.

    Root `0.85638`.
    """

    number = (1, 1, 12, 5)
    name = "Equation 5"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Gorgey, A., Azim, F. A., Zulkifly, Z. H., Hassim, H. (2025). Efficiency of Ridders' method"
            " in solving nonlinear equations using Scilab programming. Data Analytics and Applied "
            "Mathematics 6(1), 23–35. https://doi.org/10.15282/daam.v6i1.11307."
        ),
        location="Equation 5",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 2.0 * c
        return x * math.sin(x) - x**2 * math.exp(x) + math.exp(-x) + math.cos(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=2.4614018212019135),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=3.456885873702464),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
