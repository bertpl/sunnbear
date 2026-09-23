"""Category 3 holds custom formulas built to provoke specific solver behavior."""

from sunnbear._core.functions.core import FormulaCategory


class CustomFunctions(FormulaCategory):
    """`CustomFunctions` is the top-level category of custom formulas built to provoke specific solver behavior."""

    number = (3,)
    name = "Custom functions"
    is_builtin_only = True
