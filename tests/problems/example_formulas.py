"""This module defines 2 example formulas for the tests of the framework, under the user-defined category 99.

Tests of the framework use these formulas, not shipped ones, so that a change to the shipped catalog leaves those
tests as they are.

Importing this module registers both formulas. The root `conftest.py` imports it, so every test process has them, and
a worker process of a benchmark or pipeline run imports it by its module name. The `isolated_formula_registry`
fixture leaves both formulas out of its copy of the registry.
"""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamGrid, ParamRecipe


# ==================================================================================================
#  ExampleCubic
# ==================================================================================================
class ExampleCubic(Formula):
    """`ExampleCubic` is the cubic ``x^3 - p1*x - c``, on a fixed interval, with 6 values of ``p1``."""

    number = (99, 801)
    name = "Example cubic"
    param_names = ("p1",)

    @staticmethod
    def parametrized_fun(x: float, c: float, p1: float) -> float:
        """Evaluate ``x^3 - p1*x - c``."""
        return x * x * x - p1 * x - c

    def interval_bounds(self, p1: float) -> tuple[float, float]:
        """Return the interval ``[-2, 2]``, which every parameter tuple shares."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``p1`` from 0 to 1 in steps of 0.2."""
        return (ParamGrid.decimal("p1", 0.0, 1.0, step=0.2),)

    test_cases = (
        FormulaTestCase.value(params={"p1": 0.0}, x=0.0, c=0.0, expected=0.0),  # root at the origin
        FormulaTestCase.value(params={"p1": 1.0}, x=2.0, c=1.0, expected=5.0),  # 8 - 2 - 1
        FormulaTestCase.interval_bounds(params={"p1": 0.0}, expected=(-2.0, 2.0)),
    )


# ==================================================================================================
#  ExampleOddPower
# ==================================================================================================
class ExampleOddPower(Formula):
    """`ExampleOddPower` is the odd power ``x^p1 - c``, which accepts only an odd integer ``p1``."""

    number = (99, 802)
    name = "Example odd power"
    param_names = ("p1",)

    @staticmethod
    def parametrized_fun(x: float, c: float, p1: float) -> float:
        """Evaluate ``x^p1 - c``."""
        return x**p1 - c

    def interval_bounds(self, p1: float) -> tuple[float, float]:
        """Return the interval ``[-2, 2]``, which every parameter tuple shares."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``p1`` over the odd integers from 1 to 7."""
        return (ParamGrid.decimal("p1", 1.0, 7.0, step=2.0),)

    def is_param_tuple_valid(self, p1: float) -> bool:
        """Require ``p1`` to be an odd integer, because an even power has no sign change on the interval."""
        return p1 == int(p1) and int(p1) % 2 == 1

    test_cases = (
        FormulaTestCase.value(params={"p1": 3.0}, x=2.0, c=8.0, expected=0.0),  # 2^3 - 8, a root
        FormulaTestCase.value(params={"p1": 3.0}, x=2.0, c=0.0, expected=8.0),  # 2^3
        FormulaTestCase.invalid(params={"p1": 2.0}),  # even power
        FormulaTestCase.invalid(params={"p1": 1.5}),  # power that is not an integer
        FormulaTestCase.interval_bounds(params={"p1": 3.0}, expected=(-2.0, 2.0)),
    )
