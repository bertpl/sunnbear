"""This category holds polynomials that a reference work lists by name, such as the Legendre polynomials.

Each polynomial of the category has as many zeros as its degree ``n``, all of them inside ``[-1, 1]``. A test problem
needs a sign change over its interval, so the interval has to hold an odd number of zeros:

- an odd ``n`` takes ``[-1, 1]``, which holds every zero;
- an even ``n`` takes an interval that leaves out 1 zero, the lowest.

`helpers` holds that rule, and the degrees that every formula of the category sweeps.

In every formula but `ChebyshevFirstKindPolynomial`, ``c`` shifts ``x`` by ``c/n^2``, because the zeros next to the
bounds lie about ``1/n^2`` apart. The shifted function keeps its form and, across the calibrated range of ``c``, the
number of zeros in its interval.

Its values at the bounds of the interval do change with ``c``, and those values decide a solver's first steps.
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
