"""This category holds polynomials that a reference work lists by name, such as the Legendre polynomials.

A test problem needs a sign change over its interval, so the interval has to hold an odd number of the polynomial's
real zeros. Most polynomials of the category have as many real zeros as their degree ``n``:

- an odd ``n`` takes an interval that holds every zero;
- an even ``n`` takes an interval that leaves out 1 zero, the lowest.

`BernoulliPolynomial` is the exception: most of its zeros are complex, so it takes odd degrees only, on intervals
that its parameters give.

In every formula but `ChebyshevFirstKindPolynomial`, ``c`` moves the zeros along the x-axis: by a shift of ``x`` or,
in `SecondWilkinsonPolynomial`, by a common factor. The function then keeps its form and, across the calibrated range
of ``c``, the number of zeros in its interval.

The function's values at the bounds of the interval do change with ``c``, and those values decide a solver's first
steps.

The first 5 formulas hold the polynomials that are orthogonal on ``[-1, 1]``. They shift ``x`` by ``c/n^2``, because
their zeros next to the bounds lie about ``1/n^2`` apart. `helpers` holds what else they share: `SWEPT_DEGREES` and
the rule for their intervals.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_chebyshev_polynomial_of_the_first_kind,
    f02_chebyshev_polynomial_of_the_second_kind,
    f03_legendre_polynomial,
    f04_gegenbauer_polynomial,
    f05_jacobi_polynomial,
    f06_hermite_polynomial,
    f07_laguerre_polynomial,
    f08_bernoulli_polynomial,
    f09_wilkinson_polynomial,
    f10_second_wilkinson_polynomial,
)


class NamedPolynomials(FormulaCategory):
    """`NamedPolynomials` is the category of polynomials that a reference work lists by name."""

    number = (2, 2)
    name = "Named polynomials"
