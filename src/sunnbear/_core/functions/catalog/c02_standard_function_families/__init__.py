"""This category holds standard function families."""

from sunnbear._core.functions.core import FormulaCategory

from . import c01_polynomials


class StandardFunctionFamilies(FormulaCategory):
    """`StandardFunctionFamilies` is the top-level category of standard function families."""

    number = (2,)
    name = "Standard function families"
    is_builtin_only = True
