"""This category holds formulas written for sunnbear, to provoke specific solver behavior."""

from sunnbear._core.problems.core import FormulaCategory


class PurposeBuiltFunctions(FormulaCategory):
    """`PurposeBuiltFunctions` is the top-level category of formulas written for sunnbear."""

    number = (3,)
    name = "Purpose-built functions"
    description = (
        "The test problems are functions written for sunnbear, each to provoke a specific behavior of a solver."
    )
    is_builtin_only = True
