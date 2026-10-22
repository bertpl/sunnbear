"""This module holds the formula of 3 in Chandrupatla (1997).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1997_chandrupatla`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "9bb6f377d039c9c1"


class Chandrupatla19973(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``(x - 3)^3``; the formula's interval is `[0, 5]`; `[-10, 10]`; `[-1E4, 1E4]`; `[-1E6, 1E6]`;
    `[-1E10, 1E10]`.

    Printed zero: `x = 3`.
    """

    number = (1, 1, 7, 3)
    name = "3"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return (x - 3) ** 3

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
                        0.0,
                        5.0,
                    ),
                    (
                        -10.0,
                        10.0,
                    ),
                    (
                        -10000.0,
                        10000.0,
                    ),
                    (
                        -1000000.0,
                        1000000.0,
                    ),
                    (
                        -10000000000.0,
                        10000000000.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 5.0}, x=1.5, c=0.0, expected=-3.375),
        FormulaTestCase.value(params={"a": 0.0, "b": 5.0}, x=1.5, c=0.25, expected=-20.796875),
        FormulaTestCase.value(params={"a": -10.0, "b": 10.0}, x=-4.0, c=0.0, expected=-343.0),
        FormulaTestCase.value(params={"a": -10000.0, "b": 10000.0}, x=-4000.0, c=0.0, expected=-64144108027.0),
        FormulaTestCase.value(
            params={"a": -1000000.0, "b": 1000000.0}, x=-400000.0, c=0.0, expected=-6.4001440010800024e16
        ),
        FormulaTestCase.value(
            params={"a": -10000000000.0, "b": 10000000000.0}, x=-4000000000.0, c=0.0, expected=-6.4000000144e28
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 5.0}, expected=(0.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -10000.0, "b": 10000.0}, expected=(-10000.0, 10000.0)),
        FormulaTestCase.interval_bounds(params={"a": -1000000.0, "b": 1000000.0}, expected=(-1000000.0, 1000000.0)),
        FormulaTestCase.interval_bounds(
            params={"a": -10000000000.0, "b": 10000000000.0}, expected=(-10000000000.0, 10000000000.0)
        ),
    )
