"""This category holds polynomial formulas.

Every formula of the category adds ``c`` to the function value, and at ``c = 0`` its values at the bounds of its
interval are the same for every parameter tuple. The calibrated range of ``c`` is therefore the same for all of a
formula's test problems.

The category holds polynomials only: a power function with a fractional or negative exponent is not one.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_linear,
    f02_linear_plus_even_power,
    f03_linear_plus_odd_power,
    f04_linear_plus_sum_of_even_powers,
    f05_linear_plus_sum_of_odd_powers,
    f06_one_sided_linear_plus_power,
)


class Polynomials(FormulaCategory):
    """`Polynomials` is the category of polynomial formulas."""

    number = (2, 1)
    name = "Polynomials"
