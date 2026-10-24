"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.3`` in the survey of published test problems. A script generates this
module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/` and
run `uv run python -m scripts.literature_test_problems.formula_modules 2025_romadani_python_implementations`; do not
edit this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "c04fa7500d8056f8"


class Romadani202553(Formula):
    """This formula comes from Romadani (2025).

    The survey writes the source's function as ``exp(-x) - exp(-2*x) - exp(-3*x)``; the formula's intervals are `[0, 1]`
    (the bracketing methods), `[-2, 2]` (the search for the exact root) and `[-2, 60]` (the global analysis).

    Stated root `0.481211825060`. The article also states a second root near `x = 56.27` on `[-2, 60]`; the function
    equals `exp(-x)*(1 - exp(-x) - exp(-2*x))`, which has no root other than the first.
    """

    number = (1, 2, 17, 3)
    name = "5.3"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Romadani, M. N. H. (2025). From Theory to Code: Transforming Classical Root-Finding "
            "Methods into Efficient Python Implementations. ICCK Journal of Applied Mathematics 1(3), "
            "154–189. https://doi.org/10.62762/jam.2025.840767."
        ),
        location="5.3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(-x) - math.exp(-2 * x) - math.exp(-3 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((0.0, 1.0, 1.0), (-2.0, 2.0, 4.0), (-2.0, 60.0, 62.0))),)

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=-0.2145630751529077),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=-0.8143159699603034),
        FormulaTestCase.value(params={"a": -2.0, "b": 2.0, "c_scale": 4.0}, x=-0.8, c=0.0, expected=-13.75066787654425),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 60.0, "c_scale": 62.0}, x=16.6, c=0.0, expected=6.176060954143003e-08
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 2.0, "c_scale": 4.0}, expected=(-2.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 60.0, "c_scale": 62.0}, expected=(-2.0, 60.0)),
    )
