"""Documented function families (category 2)."""

from sunnbear._core.functions.core import FormulaCategory

from . import c01_polynomials


class DocumentedFunctions(FormulaCategory):
    """Top-level category of documented function families."""

    number = (2,)
    name = "Documented functions"
    is_builtin_only = True
