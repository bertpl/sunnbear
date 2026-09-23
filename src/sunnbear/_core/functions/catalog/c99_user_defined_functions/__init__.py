"""This package holds the top-level category for user formulas, empty in sunnbear itself.

Users register their own categories and formulas under it, e.g. a category numbered
``(USER_DEFINED_FORMULA_CATEGORY_NUMBER, 1)``.
"""

from sunnbear._core.functions.core import USER_DEFINED_FORMULA_CATEGORY_NUMBER, FormulaCategory


class UserDefinedFunctions(FormulaCategory):
    """`UserDefinedFunctions` is the top-level category of formulas defined outside sunnbear."""

    number = (USER_DEFINED_FORMULA_CATEGORY_NUMBER,)
    name = "User-defined functions"
