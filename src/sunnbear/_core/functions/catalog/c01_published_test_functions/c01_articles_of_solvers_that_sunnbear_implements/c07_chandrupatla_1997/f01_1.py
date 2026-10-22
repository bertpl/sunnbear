"""This module holds the formula of 1 in Chandrupatla (1997).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1997_chandrupatla`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "86dbdfd5af6ae2ca"


class Chandrupatla19971(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``x^3 - 2*x - 5``; the formula's interval is `[2, 3]`; `[1, 10]`; `[1, 100]`; `[-1E4, 1E4]`;
    `[-1E10, 1E10]`.

    Printed zero: `x = 2.0945515`. The article calls it "extensively tried out in the literature". Its appendix program
    evaluates this function.
    """

    number = (1, 1, 7, 1)
    name = "1"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return x**3 - 2 * x - 5

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
                        2.0,
                        3.0,
                    ),
                    (
                        1.0,
                        10.0,
                    ),
                    (
                        1.0,
                        100.0,
                    ),
                    (
                        -10000.0,
                        10000.0,
                    ),
                    (
                        -10000000000.0,
                        10000000000.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": 2.0, "b": 3.0}, x=2.3, c=0.0, expected=2.5669999999999975),
        FormulaTestCase.value(params={"a": 2.0, "b": 3.0}, x=2.3, c=0.25, expected=-0.4848750000000019),
        FormulaTestCase.value(params={"a": 1.0, "b": 10.0}, x=3.7, c=0.0, expected=38.25300000000001),
        FormulaTestCase.value(params={"a": 1.0, "b": 100.0}, x=30.7, c=0.0, expected=28868.042999999998),
        FormulaTestCase.value(params={"a": -10000.0, "b": 10000.0}, x=-4000.0, c=0.0, expected=-63999992005.0),
        FormulaTestCase.value(
            params={"a": -10000000000.0, "b": 10000000000.0}, x=-4000000000.0, c=0.0, expected=-6.4e28
        ),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 3.0}, expected=(2.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 10.0}, expected=(1.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 100.0}, expected=(1.0, 100.0)),
        FormulaTestCase.interval_bounds(params={"a": -10000.0, "b": 10000.0}, expected=(-10000.0, 10000.0)),
        FormulaTestCase.interval_bounds(
            params={"a": -10000000000.0, "b": 10000000000.0}, expected=(-10000000000.0, 10000000000.0)
        ),
    )
