"""Helpers that define throwaway formula and category classes for the tests of the test-function layer.

Defining a formula or category class registers it, so a test that calls these helpers uses the
``isolated_registry`` fixture.
"""

from sunnbear._core.functions.core.taxonomy import format_taxonomy_number
from sunnbear.functions import Formula, FormulaCategory, ParamRecipe


def define_formula_cls(formula_number: tuple[int, ...]) -> type[Formula]:
    """Define and return a formula without parameters, numbered `formula_number`."""

    class ExampleFormula(Formula):
        number = formula_number
        name = f"Example {format_taxonomy_number(formula_number)}"
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float) -> float:
            return x - c

        def interval_bounds(self) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return ()

    return ExampleFormula


def define_category_cls(category_number: tuple[int, ...], **attrs: object) -> type[FormulaCategory]:
    """Define and return a category numbered `category_number`, with `attrs` as extra class attributes."""
    namespace = {"number": category_number, "name": f"Example {format_taxonomy_number(category_number)}", **attrs}
    return type("ExampleCategory", (FormulaCategory,), namespace)
