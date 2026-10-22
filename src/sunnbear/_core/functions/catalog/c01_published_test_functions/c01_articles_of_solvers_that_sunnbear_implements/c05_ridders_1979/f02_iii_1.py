"""This module holds the formula of III.1 in Ridders (1979).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1979_ridders`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "5eb49ebcb23c36fa"


class Ridders1979Iii1(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``x*exp(x) - 10``; the formula's interval is `[-10, 10]`; `[-100, 100]`.

    Last printed iterate: `1.745528003`.
    """

    number = (1, 1, 5, 2)
    name = "III.1"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous"
            " function. IEEE Transactions on Circuits and Systems 26(11), 979–980. "
            "https://doi.org/10.1109/TCS.1979.1084580."
        ),
        location="III.1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return x * math.exp(x) - 10

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
                        -10.0,
                        10.0,
                    ),
                    (
                        -100.0,
                        100.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0}, x=-4.0, c=0.0, expected=-10.073262555554937),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0}, x=-4.0, c=0.25, expected=-10.00111068823678),
        FormulaTestCase.value(params={"a": -100.0, "b": 100.0}, x=-40.0, c=0.0, expected=-10.0),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -100.0, "b": 100.0}, expected=(-100.0, 100.0)),
    )
