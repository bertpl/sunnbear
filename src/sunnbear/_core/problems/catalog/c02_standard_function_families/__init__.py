"""This category holds standard function families."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_simple_polynomials,
    c02_named_polynomials,
    c03_power_functions,
    c04_hyperbolic_functions,
    c05_exponential_and_logarithm,
)


class StandardFunctionFamilies(FormulaCategory):
    """`StandardFunctionFamilies` is the top-level category of standard function families."""

    number = (2,)
    name = "Standard function families"
    is_builtin_only = True
