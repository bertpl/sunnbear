"""This module holds the formula of Equation 1 in Gorgey et al. (2025).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2025_gorgey`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "5f0d788d8363c35a"


class GorgeyEtAl2025Equation1(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``(x + 2)*(x + 1)*(x - 3)^3``; the formula's interval is `[-2.5, 3]`; `[2, 3.5]` (the text below
    Table 2).

    Roots `-2`, `-1` and `3`; the text names `3` as the root found. Figure 1's caption and the text below Table 2 give
    the interval `[2, 3.5]`.
    """

    number = (1, 1, 12, 1)
    name = "Equation 1"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Gorgey, A., Azim, F. A., Zulkifly, Z. H., Hassim, H. (2025). Efficiency of Ridders' method"
            " in solving nonlinear equations using Scilab programming. Data Analytics and Applied "
            "Mathematics 6(1), 23–35. https://doi.org/10.15282/daam.v6i1.11307."
        ),
        location="Equation 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return (x + 2) * (x + 1) * (x - 3) ** 3

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b"),
                rows=(
                    (
                        -2.5,
                        3.0,
                    ),
                    (
                        2.0,
                        3.5,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": -2.5, "b": 3.0}, x=-0.85, c=0.0, expected=-9.843992812500002),
        FormulaTestCase.value(params={"a": -2.5, "b": 3.0}, x=-0.85, c=0.25, expected=-39.316739150390646),
        FormulaTestCase.value(params={"a": 2.0, "b": 3.5}, x=2.45, c=0.0, expected=-2.554272187499998),
        FormulaTestCase.interval_bounds(params={"a": -2.5, "b": 3.0}, expected=(-2.5, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 3.5}, expected=(2.0, 3.5)),
    )
