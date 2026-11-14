"""This formula is the Hermite polynomial, divided by its norm, with ``x`` shifted by ``c``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamGrid, ParamRecipe

from .helpers import is_valid_degree

# Above this degree the values at the bounds of the interval overflow.
HIGHEST_VALID_DEGREE = 512
HIGHEST_SWEPT_DEGREE = 40
# The lower bound of an even degree's interval uses this factor: ``2^(-1/3)`` times the mean of 2.338 and 4.088, the
# absolute values of the first 2 zeros of the Airy function Ai.
LOWEST_ZEROS_AIRY_FACTOR = 2.55


class HermitePolynomial(Formula):
    """`HermitePolynomial` is ``H_n(x - c)/sqrt(2^n * n! * sqrt(pi))``, with ``H_n`` the Hermite polynomial.

    ``H_n`` is the physicists' Hermite polynomial, whose weight is ``exp(-x^2)``. The probabilists' Hermite polynomial
    is the same function with ``x`` scaled by ``sqrt(2)``, so it has no formula of its own.

    ``n`` is the degree, an integer from 1 to `HIGHEST_VALID_DEGREE`. The function has ``n`` zeros in its interval for
    an odd ``n``, and ``n - 1`` for an even ``n``.

    The zeros lie inside ``[-sqrt(2*n + 1), sqrt(2*n + 1)]``, about ``pi/sqrt(2*n)`` apart in the middle. The
    amplitude grows about as ``exp(x^2/2)`` from the middle to the bounds, which is far faster than in the formulas
    whose polynomials are orthogonal on ``[-1, 1]``.

    The polynomial is divided by ``sqrt(2^n * n! * sqrt(pi))``, its norm under the weight ``exp(-x^2)``. The amplitude
    in the middle of the interval is then below 1 for every ``n``, while that of ``H_n`` itself grows with the norm.
    The division moves no zero, because it only scales the function.

    ``c`` shifts ``x`` by ``c`` itself, not by ``c/n^2`` as in the formulas whose polynomials are orthogonal on
    ``[-1, 1]``: the zeros next to the bounds lie about ``n^(-1/6)`` apart, so the calibrated range of ``c`` narrows
    only slowly as ``n`` grows.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the definition and the norm. https://dlmf.nist.gov/18.3
        - NIST Digital Library of Mathematical Functions, §18.9(i), for the recurrence. https://dlmf.nist.gov/18.9
        - NIST Digital Library of Mathematical Functions, §18.16(v), for the zeros. https://dlmf.nist.gov/18.16
    """

    number = (2, 2, 6)
    name = "Hermite polynomial"
    param_names = ("n",)

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``h_n(x - c)``, with ``h_k(y) = H_k(y)/sqrt(2^k * k! * sqrt(pi))``.

        The recurrence is ``h_(k+1)(y) = sqrt(2/(k + 1))*y*h_k(y) - sqrt(k/(k + 1))*h_(k-1)(y)``, which follows from
        the recurrence of ``H_k`` and its norm. The recurrence takes ``n`` steps and holds for every ``x``.
        """
        y = x - c
        h_previous = 0.0
        h = math.pi**-0.25
        for k in range(int(n)):
            h_previous, h = h, math.sqrt(2.0 / (k + 1)) * y * h - math.sqrt(k / (k + 1)) * h_previous
        return h

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the interval that holds every zero for an odd ``n``, and every zero but the lowest for an even ``n``.

        Every zero lies inside ``[-sqrt(2*n + 1), sqrt(2*n + 1)]``, which is the interval for an odd ``n``.

        The lower bound for an even ``n`` lies between the 2 lowest zeros, which lie near
        ``-(sqrt(2*n + 1) - 2^(-1/3)*abs(a_k)*(2*n + 1)^(-1/6))``, with ``a_k``, for ``k`` = 1 and 2, the first 2 zeros
        of the Airy function Ai. The lower bound is that expression with the mean of ``abs(a_1)`` and
        ``abs(a_2)`` in place of ``abs(a_k)``.

        That rule is an approximation; the tests check it at sampled degrees up to `HIGHEST_VALID_DEGREE`.
        """
        upper_bound = math.sqrt(2.0 * n + 1.0)
        if int(n) % 2 == 1:
            return (-upper_bound, upper_bound)
        else:
            return (-(upper_bound - LOWEST_ZEROS_AIRY_FACTOR * (2.0 * n + 1.0) ** (-1.0 / 6.0)), upper_bound)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps every degree from 1 to `HIGHEST_SWEPT_DEGREE`.

        A higher degree mainly widens the range of values between the middle of the interval and its bounds, and a
        wide range of values is not the purpose of this formula.
        """
        return (ParamGrid.decimal("n", 1.0, float(HIGHEST_SWEPT_DEGREE), 1.0),)

    def is_param_tuple_valid(self, n: float) -> bool:
        """Require ``n`` to be an integer from 1 to `HIGHEST_VALID_DEGREE`."""
        if not is_valid_degree(n):
            return False
        else:
            return n <= HIGHEST_VALID_DEGREE

    test_cases = (
        # h_1(y) = sqrt(2)*y/pi^0.25
        FormulaTestCase.value(params={"n": 1.0}, x=1.0, c=0.0, expected=math.sqrt(2.0) / math.pi**0.25),
        # h_2(y) = (4*y^2 - 2)/sqrt(8*sqrt(pi))
        FormulaTestCase.value(params={"n": 2.0}, x=1.0, c=0.0, expected=2.0 / math.sqrt(8.0 * math.sqrt(math.pi))),
        # c shifts x to y = 1
        FormulaTestCase.value(params={"n": 2.0}, x=1.5, c=0.5, expected=2.0 / math.sqrt(8.0 * math.sqrt(math.pi))),
        FormulaTestCase.invalid(params={"n": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 513.0}),  # degree above the highest one
        FormulaTestCase.interval_bounds(params={"n": 3.0}, expected=(-math.sqrt(7.0), math.sqrt(7.0))),
        FormulaTestCase.interval_bounds(params={"n": 4.0}, expected=(-(3.0 - 2.55 * 9.0 ** (-1.0 / 6.0)), 3.0)),
    )
