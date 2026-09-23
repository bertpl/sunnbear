"""This category holds polynomial formulas."""

from sunnbear._core.functions.core import FormulaCategory

from . import f01_cubic, f02_odd_power


class Polynomials(FormulaCategory):
    """`Polynomials` is the category of polynomial formulas."""

    number = (2, 1)
    name = "Polynomials"
