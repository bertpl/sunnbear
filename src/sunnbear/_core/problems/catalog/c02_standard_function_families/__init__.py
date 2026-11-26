"""This category holds standard function families."""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    c01_simple_polynomials,
    c02_named_polynomials,
    c03_power_functions,
    c04_hyperbolic_functions,
    c05_exponential_and_logarithm,
    c06_trigonometric_functions,
)


class StandardFunctionFamilies(FormulaCategory):
    """`StandardFunctionFamilies` is the top-level category of standard function families."""

    number = (2,)
    name = "Standard function families"
    description = (
        "Families of standard functions, such as polynomials, powers and the hyperbolic functions. Their parameters "
        "set what a solver has to deal with, such as roots close together, an infinite slope, a pole or exponential "
        "growth."
    )
    is_builtin_only = True
