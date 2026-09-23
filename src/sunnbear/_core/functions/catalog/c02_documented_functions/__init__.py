"""Category 2 holds documented function families."""

from sunnbear._core.functions.core import FormulaCategory

from . import c01_polynomials


class DocumentedFunctions(FormulaCategory):
    """`DocumentedFunctions` is the top-level category of documented function families."""

    number = (2,)
    name = "Documented functions"
    is_builtin_only = True
