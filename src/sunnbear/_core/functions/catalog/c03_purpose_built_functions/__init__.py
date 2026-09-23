"""This category holds formulas written for sunnbear, to provoke specific solver behavior."""

from sunnbear._core.functions.core import FormulaCategory


class PurposeBuiltFunctions(FormulaCategory):
    """`PurposeBuiltFunctions` is the top-level category of formulas written for sunnbear."""

    number = (3,)
    name = "Purpose-built functions"
    is_builtin_only = True
