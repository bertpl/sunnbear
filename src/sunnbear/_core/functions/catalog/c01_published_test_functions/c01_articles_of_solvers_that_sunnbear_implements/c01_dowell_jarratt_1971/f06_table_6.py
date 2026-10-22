"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 6`` in the survey of published test problems. A script generates
this module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/`
and run `uv run python -m scripts.literature_test_problems.formula_modules 1971_dowell_jarratt_illinois`; do not edit
this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "db43ba3a20c3e339"


class DowellJarratt1971Table6(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``exp(-n*x)*(x - 1) + x^n``, with the parameters ``n = 1, 5, 10, 15``;
    the formula's interval is ``[0, 1]``.

    The caption says the curves lie closer to the x-axis as `n` grows.
    """

    number = (1, 1, 1, 6)
    name = "Table 6"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1.0 * c
        return math.exp(-n * x) * (x - 1) + x**n

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("n",), rows=((1.0,), (5.0,), (10.0,), (15.0,))),)

    cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=-0.21857275447720254),
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.25, expected=-0.8536679532756783),
        FormulaTestCase.value(params={"n": 5.0}, x=0.3, c=0.0, expected=-0.1537611121039009),
        FormulaTestCase.value(params={"n": 10.0}, x=0.3, c=0.0, expected=-0.03484504295750476),
        FormulaTestCase.value(params={"n": 15.0}, x=0.3, c=0.0, expected=-0.007776283227862616),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(0.0, 1.0)),
    )
