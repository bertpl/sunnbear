"""Polynomial formulas (category 2.1)."""

from sunnbear._core.functions.core import FormulaCategory

from . import f01_cubic, f02_odd_power


class Polynomials(FormulaCategory):
    """Category of polynomial formulas."""

    number = (2, 1)
    name = "Polynomials"
