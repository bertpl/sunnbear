"""This module defines helpers that create throwaway formula and category classes for the tests of the
test-problem layer.

Defining a formula or category class registers it, so a test that calls these helpers uses the
``isolated_formula_registry`` fixture.
"""

from sunnbear._core.problems.core import Formula, FormulaCategory, ParamRecipe
from sunnbear._core.problems.core.taxonomy import FormulaTaxonomyNode


def define_formula_cls(formula_number: tuple[int, ...]) -> type[Formula]:
    """Define and return a formula without parameters, numbered `formula_number`."""

    class ExampleFormula(Formula):
        number = formula_number
        name = f"Example {FormulaTaxonomyNode.format_number(formula_number)}"
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float) -> float:
            """Return ``x - c``, so the root is at ``c``."""
            return x - c

        def interval_bounds(self) -> tuple[float, float]:
            """Return the interval ``[-1, 1]``."""
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            """Return no recipes; the formula has no parameters."""
            return ()

    return ExampleFormula


def define_category_cls(category_number: tuple[int, ...], **attrs: object) -> type[FormulaCategory]:
    """Define and return a category numbered `category_number`, with `attrs` as extra class attributes."""
    namespace = {
        "number": category_number,
        "name": f"Example {FormulaTaxonomyNode.format_number(category_number)}",
        **attrs,
    }
    return type("ExampleCategory", (FormulaCategory,), namespace)
