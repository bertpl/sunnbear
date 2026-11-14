"""This category holds polynomials that a reference work lists by name, such as the Legendre polynomials.

Each polynomial of the category has as many zeros as its degree ``n``, all of them inside ``[-1, 1]``. A test problem
needs a sign change over its interval, so the interval has to hold an odd number of zeros:

- an odd ``n`` takes ``[-1, 1]``, which holds every zero;
- an even ``n`` takes an interval that leaves out 1 zero, the lowest.

`helpers` holds that rule, and the degrees that every formula of the category sweeps.

In most formulas ``c`` shifts ``x``. The function then keeps its form and every zero of its interval for every ``c``,
while its values at the bounds of the interval change with ``c``, and those values decide a solver's first steps.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_chebyshev_polynomial_of_the_first_kind,
    f02_chebyshev_polynomial_of_the_second_kind,
    f03_legendre_polynomial,
    f04_gegenbauer_polynomial,
    f05_jacobi_polynomial,
)


class NamedPolynomials(FormulaCategory):
    """`NamedPolynomials` is the category of polynomials that a reference work lists by name."""

    number = (2, 2)
    name = "Named polynomials"
