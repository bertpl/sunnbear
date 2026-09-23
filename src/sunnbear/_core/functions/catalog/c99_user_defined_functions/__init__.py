"""This package holds the top-level category for user formulas, empty in sunnbear itself.

Users register their own categories and formulas under it, e.g. a category ``(99, 1)``.
"""

from sunnbear._core.functions.core import FormulaCategory


class UserDefinedFunctions(FormulaCategory):
    """`UserDefinedFunctions` is the top-level category of formulas defined outside sunnbear."""

    number = (99,)
    name = "User-defined functions"
