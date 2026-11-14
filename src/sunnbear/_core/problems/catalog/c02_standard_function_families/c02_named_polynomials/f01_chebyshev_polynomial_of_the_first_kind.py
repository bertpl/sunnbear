"""This formula is the Chebyshev polynomial of the first kind with ``c`` added to it, ``T_n(x) + c``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe, ParamTable

from .helpers import JACOBI_SWEPT_DEGREES, is_valid_degree, jacobi_interval_bounds


class ChebyshevFirstKindPolynomial(Formula):
    """`ChebyshevFirstKindPolynomial` is ``T_n(x) + c``, with ``T_n`` the Chebyshev polynomial of the first kind.

    ``n`` is the degree, an integer of at least 1. The function has ``n`` zeros in its interval for an odd ``n``, and
    ``n - 1`` for an even ``n``. ``n = 1`` gives the line ``x + c``.

    ``T_n`` oscillates between -1 and 1 across the whole of ``[-1, 1]``.

    For every ``c`` between -1 and 1 the function therefore keeps the same number of zeros in its interval, and ``c``
    only moves them. That is why ``c`` adds to the function value here, while it shifts ``x`` in the other formulas of
    the category.

    At ``c = 0`` the function goes from -1 at the lower bound to 1 at the upper bound, for every ``n``. For an odd
    ``n``, ``T_n(-1)`` is -1. For an even ``n``, the lower bound of the interval is the smallest ``x`` inside
    ``[-1, 1]`` at which ``T_n`` is -1.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the definition. https://dlmf.nist.gov/18.3
        - NIST Digital Library of Mathematical Functions, §18.5(i), for the trigonometric form. https://dlmf.nist.gov/18.5
    """

    number = (2, 2, 1)
    name = "Chebyshev polynomial of the first kind"
    param_names = ("n",)

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``T_n(x) + c``, with ``T_n(x)`` as ``cos(n*acos(x))``.

        ``cos(n*acos(x))`` is defined only on ``[-1, 1]``, where it equals the polynomial and costs the same for every
        ``n``.
        """
        return math.cos(n * math.acos(x)) + c

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return ``[-1, 1]`` for an odd ``n``, and ``[-cos(pi/n), 1]`` for an even ``n``.

        ``T_n`` is the Jacobi polynomial with both parameters -0.5, up to a constant factor.
        """
        return jacobi_interval_bounds(n, -0.5, -0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps the degrees of `JACOBI_SWEPT_DEGREES`."""
        return (ParamTable(names=self.param_names, rows=tuple((degree,) for degree in JACOBI_SWEPT_DEGREES)),)

    def is_param_tuple_valid(self, n: float) -> bool:
        """Require ``n`` to be an integer of at least 1."""
        return is_valid_degree(n)

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.5, c=0.0, expected=-0.5),  # T_2(x) = 2*x^2 - 1
        FormulaTestCase.value(params={"n": 2.0}, x=0.5, c=0.25, expected=-0.25),  # c shifts the value
        FormulaTestCase.value(params={"n": 3.0}, x=-1.0, c=0.0, expected=-1.0),  # T_3(-1) = -1
        FormulaTestCase.value(params={"n": 4.0}, x=-math.sqrt(0.5), c=0.0, expected=-1.0),  # at its lower bound
        FormulaTestCase.invalid(params={"n": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 0.0}),  # degree below 1
        FormulaTestCase.interval_bounds(params={"n": 3.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"n": 4.0}, expected=(-math.sqrt(0.5), 1.0)),  # -cos(pi/4)
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.0)),
    )
