"""Custom formulas built to provoke specific solver behavior (category 3)."""

from sunnbear._core.functions.core import FormulaCategory


class CustomFunctions(FormulaCategory):
    """Top-level category of custom formulas built to provoke specific solver behavior."""

    number = (3,)
    name = "Custom functions"
    is_builtin_only = True
