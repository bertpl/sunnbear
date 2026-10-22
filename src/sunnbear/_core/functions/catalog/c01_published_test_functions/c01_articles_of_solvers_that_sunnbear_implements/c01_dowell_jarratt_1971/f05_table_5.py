"""This module holds the formula of Table 5 in Dowell, Jarratt (1971).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1971_dowell_jarratt_illinois`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "ac3c369aa3cc68df"


class DowellJarratt1971Table5(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``(1 + (1 - n)^4)*x - (1 - n*x)^4``, with the parameters ``n = 2, 5, 15, 20``; the formula's
    interval is ``[0, 1]``.

    The caption says the function has 1 turning point and 1 inflection point on `[0, 1]`.
    """

    number = (1, 1, 1, 5)
    name = "Table 5"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 5",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1.0 * c
        return (1 + (1 - n) ** 4) * x - (1 - n * x) ** 4

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((2.0,), (5.0,), (15.0,), (20.0,))),)

    cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.0, expected=0.5744),
        FormulaTestCase.value(params={"n": 2.0}, x=0.3, c=0.25, expected=-0.5561),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=77.0375),
        FormulaTestCase.value(params={"n": 15.0}, x=0.3, c=0.0, expected=11375.0375),
        FormulaTestCase.value(params={"n": 20.0}, x=0.3, c=0.0, expected=38471.6),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
