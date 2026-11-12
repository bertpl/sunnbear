"""This category holds polynomial formulas.

Every formula of the category uses the interval ``[-1, 1]``, adds ``c`` to the function value, and passes through
``(-1, -1)`` and ``(1, 1)`` at ``c = 0``. The category holds polynomials only: a power function with a fractional or
negative exponent is not one.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_linear,
    f02_linear_plus_even_power,
    f03_linear_plus_odd_power,
    f04_linear_plus_sum_of_even_powers,
    f05_linear_plus_sum_of_odd_powers,
)


class Polynomials(FormulaCategory):
    """`Polynomials` is the category of polynomial formulas."""

    number = (2, 1)
    name = "Polynomials"
