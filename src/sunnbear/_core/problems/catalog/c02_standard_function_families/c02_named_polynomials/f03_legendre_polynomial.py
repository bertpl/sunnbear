"""This formula is the Legendre polynomial with ``x`` shifted by ``c``, ``P_n(x - c/n^2)``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe, ParamTable

from .helpers import SWEPT_DEGREES, is_valid_degree, jacobi_interval_bounds


class LegendrePolynomial(Formula):
    """`LegendrePolynomial` is ``P_n(x - c/n^2)``, with ``P_n`` the Legendre polynomial.

    ``n`` is the degree, an integer of at least 1. The function has ``n`` zeros in its interval for an odd ``n``, and
    ``n - 1`` for an even ``n``.

    The amplitude of ``P_n`` grows from about ``sqrt(2/(pi*n))`` in the middle of ``[-1, 1]`` to 1 at the bounds -1
    and 1.

    ``c`` shifts ``x``, so the function keeps its form and, across the range of ``c``, the number of zeros in its
    interval.

    Adding ``c`` to the function value would not keep the number of zeros in the interval: the amplitude in the middle
    of ``[-1, 1]`` shrinks as ``n`` grows, so for a high degree nearly every ``c`` would leave only the zeros near the
    bounds.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the definition. https://dlmf.nist.gov/18.3
        - NIST Digital Library of Mathematical Functions, §18.9(i), for the recurrence. https://dlmf.nist.gov/18.9
    """

    number = (2, 2, 3)
    name = "Legendre polynomial"
    param_names = ("n",)

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``P_n(x - c/n^2)`` by ``(k + 1)*P_(k+1)(y) = (2*k + 1)*y*P_k(y) - k*P_(k-1)(y)``.

        The recurrence takes ``n`` steps and holds for every ``x``.
        """
        y = x - c / (n * n)
        p_previous = 1.0
        p = y
        for k in range(1, int(n)):
            p_previous, p = p, ((2 * k + 1) * y * p - k * p_previous) / (k + 1)
        return p

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return ``[-1, 1]`` for an odd ``n``, and ``[-cos(2.5*pi/(2*n + 1)), 1]`` for an even ``n``.

        ``P_n`` is the Jacobi polynomial with both parameters 0.
        """
        return jacobi_interval_bounds(n, 0.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps the degrees of `SWEPT_DEGREES`."""
        return (ParamTable(names=self.param_names, rows=tuple((degree,) for degree in SWEPT_DEGREES)),)

    def is_param_tuple_valid(self, n: float) -> bool:
        """Require ``n`` to be an integer of at least 1."""
        return is_valid_degree(n)

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=0.3, c=0.0, expected=0.3),  # P_1(y) = y
        FormulaTestCase.value(params={"n": 2.0}, x=0.5, c=0.0, expected=-0.125),  # P_2(y) = (3*y^2 - 1)/2
        FormulaTestCase.value(params={"n": 2.0}, x=1.0, c=2.0, expected=-0.125),  # c shifts x by c/4, to y = 0.5
        FormulaTestCase.value(params={"n": 3.0}, x=0.5, c=0.0, expected=-0.4375),  # P_3(y) = (5*y^3 - 3*y)/2
        FormulaTestCase.invalid(params={"n": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 0.0}),  # degree below 1
        FormulaTestCase.interval_bounds(params={"n": 3.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"n": 4.0}, expected=(-math.cos(2.5 * math.pi / 9.0), 1.0)),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
