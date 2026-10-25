"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.4`` in the survey of published test problems. A script generates this
module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/` and
run `uv run python -m scripts.literature_test_problems.formula_modules 2025_romadani_python_implementations`; do not
edit this file.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "f438a03094b8f6f6"


class Romadani202554(Formula):
    """This formula comes from Romadani (2025).

    The survey writes the source's function as ``cos(exp(x/2))^3 - x^3``; the formula's intervals are `[0, 1]` (the
    bracketing methods) and `[-1, 1]` (the search for the exact root).

    Printed as `cos^3(e^(x/2)) - x^3`. Stated root `0.363177127637`.
    """

    number = (1, 2, 17, 4)
    name = "5.4"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Romadani, M. N. H. (2025). From Theory to Code: Transforming Classical Root-Finding "
            "Methods into Efficient Python Implementations. ICCK Journal of Applied Mathematics 1(3), "
            "154–189. https://doi.org/10.62762/jam.2025.840767."
        ),
        location="5.4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.cos(math.exp(x / 2)) ** 3 - x**3

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((0.0, 1.0, 1.0), (-1.0, 1.0, 2.0))),)

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=0.03588203867309906),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=0.13953564474479144),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.0, expected=0.38282008000056855
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, expected=(-1.0, 1.0)),
    )
