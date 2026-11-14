"""This formula is the Laguerre polynomial with ``x`` shifted by ``c``, ``L_n(x - c)``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamGrid, ParamRecipe

from .helpers import is_valid_degree

# Above this degree the value at the upper bound of the interval overflows.
HIGHEST_VALID_DEGREE = 256
HIGHEST_SWEPT_DEGREE = 20


class LaguerrePolynomial(Formula):
    """`LaguerrePolynomial` is ``L_n(x - c)``, with ``L_n`` the Laguerre polynomial.

    ``n`` is the degree, an integer from 1 to `HIGHEST_VALID_DEGREE`. The function has ``n`` zeros in its interval for
    an odd ``n``, and ``n - 1`` for an even ``n``.

    The zeros lie between 0 and ``4*n + 2``, and the 2 ends of that interval are unlike each other:

    - next to 0, the zeros lie about ``1/n`` apart and the amplitude stays below 1;
    - toward ``4*n + 2``, the zeros spread out and the amplitude grows about as ``exp(x/2)``.

    ``c`` shifts ``x`` by ``c`` itself, not by ``c/n^2`` as in the formulas whose polynomials are orthogonal on
    ``[-1, 1]``. The calibrated range of ``c`` then differs between an odd and an even ``n``:

    - for an odd ``n``, ``c`` can shift the function far to the right, where the zeros lie far apart, and only a
      little to the left, where the lowest zero lies close to the lower bound 0;
    - for an even ``n``, the lower bound lies between 2 of the close zeros next to 0, which limits the shift in both
      directions.

    The polynomial is not divided by a constant, because its amplitude next to 0 already stays below 1:
    ``L_n(0) = 1`` for every ``n``.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the definition. https://dlmf.nist.gov/18.3
        - NIST Digital Library of Mathematical Functions, §18.9(i), for the recurrence. https://dlmf.nist.gov/18.9
        - NIST Digital Library of Mathematical Functions, §18.16(iv), for the zeros. https://dlmf.nist.gov/18.16
    """

    number = (2, 2, 7)
    name = "Laguerre polynomial"
    param_names = ("n",)

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``L_n(x - c)`` by ``(k + 1)*L_(k+1)(y) = (2*k + 1 - y)*L_k(y) - k*L_(k-1)(y)``.

        The recurrence takes ``n`` steps and holds for every ``x``.
        """
        y = x - c
        value_previous = 0.0
        value = 1.0
        for k in range(int(n)):
            value_previous, value = value, ((2 * k + 1 - y) * value - k * value_previous) / (k + 1)
        return value

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the interval that holds every zero for an odd ``n``, and every zero but the lowest for an even ``n``.

        Every zero lies inside ``[0, 4*n + 2]``, which is the interval for an odd ``n``.

        The lower bound for an even ``n`` lies between the 2 lowest zeros, which lie near ``j_1^2/(4*n + 2)`` and
        ``j_2^2/(4*n + 2)``, with ``j_1`` and ``j_2`` the first 2 positive zeros of the Bessel function of order 0.

        McMahon's approximation puts the midpoint of ``j_1`` and ``j_2`` at ``1.25*pi``, so the lower bound is
        ``(1.25*pi)^2/(4*n + 2)``.

        That rule is an approximation; the tests check that it holds up to `HIGHEST_VALID_DEGREE`.
        """
        upper_bound = 4.0 * n + 2.0
        if int(n) % 2 == 1:
            return (0.0, upper_bound)
        else:
            return ((1.25 * math.pi) ** 2 / upper_bound, upper_bound)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps every degree from 1 to `HIGHEST_SWEPT_DEGREE`.

        A higher degree mainly widens the range of values between the 2 ends of the interval, and a wide range of
        values is not the purpose of this formula.

        The sweep ends where the range of values is about as wide as at the highest degree that the recipe of
        `HermitePolynomial` sweeps.
        """
        return (ParamGrid.decimal("n", 1.0, float(HIGHEST_SWEPT_DEGREE), 1.0),)

    def is_param_tuple_valid(self, n: float) -> bool:
        """Require ``n`` to be an integer from 1 to `HIGHEST_VALID_DEGREE`."""
        if not is_valid_degree(n):
            return False
        else:
            return n <= HIGHEST_VALID_DEGREE

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.25, c=0.0, expected=0.75),  # L_1(y) = 1 - y
        FormulaTestCase.value(params={"n": 2.0}, x=1.0, c=0.0, expected=-0.5),  # L_2(y) = (y^2 - 4*y + 2)/2
        FormulaTestCase.value(params={"n": 2.0}, x=1.5, c=0.5, expected=-0.5),  # c shifts x to y = 1
        FormulaTestCase.value(params={"n": 3.0}, x=0.0, c=0.0, expected=1.0),  # L_n(0) = 1
        FormulaTestCase.invalid(params={"n": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 257.0}),  # degree above the highest one
        FormulaTestCase.interval_bounds(params={"n": 3.0}, expected=(0.0, 14.0)),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=((1.25 * math.pi) ** 2 / 10.0, 10.0)),
    )
