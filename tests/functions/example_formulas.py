"""The throwaway formula and category classes that the test-function tests define.

Defining one registers it, so a test that calls these helpers uses the ``isolated_registry`` fixture.
"""

from sunnbear._core.functions.core.taxonomy import format_number
from sunnbear.functions import Formula, FormulaCategory, ParamRecipe


def minimal_formula_cls(formula_number: tuple[int, ...]) -> type[Formula]:
    """Define and return a formula without parameters, numbered `formula_number`."""

    class Minimal(Formula):
        number = formula_number
        name = f"Minimal {format_number(formula_number)}"
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float) -> float:
            return x - c

        def interval_bounds(self) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return ()

    return Minimal


def category_cls(category_number: tuple[int, ...], **attrs: object) -> type[FormulaCategory]:
    """Define and return a category numbered `category_number`, with `attrs` as extra class attributes."""
    namespace = {"number": category_number, "name": f"Example {format_number(category_number)}", **attrs}
    return type("ExampleCategory", (FormulaCategory,), namespace)
