"""This formula is the Gegenbauer polynomial, divided by its value at 1, with ``x`` shifted by ``c``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamRecipe

from .helpers import degree_sweep_recipe, is_valid_degree, jacobi_interval_bounds

# ``alpha`` has to be above this value: the Gegenbauer polynomials are orthogonal on ``[-1, 1]`` only above it, and at
# this value their outermost zeros lie on the bounds -1 and 1.
ALPHA_LOWER_LIMIT = -0.5
# The tests check the rule of `jacobi_interval_bounds` up to this ``alpha``; the rule fails a little above it.
HIGHEST_ALPHA = 7.0


class GegenbauerPolynomial(Formula):
    """`GegenbauerPolynomial` is ``C_n^(alpha)(y)/C_n^(alpha)(1)`` at ``y = x - c/n^2``.

    ``C_n^(alpha)`` is the Gegenbauer polynomial, which is also called the ultraspherical polynomial.

    - ``n`` is the degree, an integer of at least 1. The function has ``n`` zeros in its interval for an odd ``n``,
      and ``n - 1`` for an even ``n``.
    - ``alpha`` sets how the swings change from the middle of ``[-1, 1]`` to its bounds. Below 0 the swings shrink
      toward the bounds, at 0 they are equally high everywhere, and above 0 they grow toward the bounds, faster for
      a higher ``alpha``. It lies above `ALPHA_LOWER_LIMIT` and is at most `HIGHEST_ALPHA`. It is not the ``alpha`` of
      `JacobiPolynomial`, which is 0.5 lower for the same polynomial.

    3 values of ``alpha`` give the polynomial of another formula: 0 gives ``T_n``, 0.5 gives the Legendre polynomial
    and 1 gives ``U_n/(n + 1)``.

    The polynomial is divided by its value at 1 for 2 reasons:

    - The function is then 1 at ``y = 1`` for every ``n`` and ``alpha``. ``C_n^(alpha)(1)`` itself is negative for an
      ``alpha`` below 0, so without the division the function would rise toward 1 for one ``alpha`` and fall for
      another.
    - The divided polynomial has a limit at ``alpha = 0``, which is ``T_n``, while ``C_n^(0)`` itself is 0 everywhere.

    The division moves no zero, because it only scales the function.

    ``c`` shifts ``x``, for the reason that `ChebyshevSecondKindPolynomial` gives: the function keeps its form and
    every zero of its interval for every ``c``.

    `parametrized_fun` evaluates the divided polynomial by a recurrence over the degrees, which takes ``n`` steps,
    holds for every ``x`` and needs no separate case at ``alpha = 0``.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the definition, where the parameter is called
          lambda; §18.6(i), for the value at 1; and §18.9(i), for the recurrence. https://dlmf.nist.gov/18.3,
          https://dlmf.nist.gov/18.6 and https://dlmf.nist.gov/18.9
    """

    number = (2, 2, 4)
    name = "Gegenbauer polynomial"
    param_names = ("n", "alpha")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, alpha: float) -> float:
        """Evaluate ``R_n(x - c/n^2)``, with ``R_k(y) = C_k^(alpha)(y)/C_k^(alpha)(1)``.

        The recurrence is ``(k + 2*alpha - 1)*R_k(y) = 2*(k + alpha - 1)*y*R_(k-1)(y) - (k - 1)*R_(k-2)(y)``, which
        follows from the recurrence of ``C_k^(alpha)`` and its value at 1.
        """
        y = x - c / (n * n)
        r_previous = 1.0
        r = y
        for k in range(2, int(n) + 1):
            r_previous, r = r, (2.0 * (k + alpha - 1.0) * y * r - (k - 1.0) * r_previous) / (k + 2.0 * alpha - 1.0)
        return r

    def interval_bounds(self, n: float, alpha: float) -> tuple[float, float]:
        """Return ``[-1, 1]`` for an odd ``n``, and ``[-cos((1 + alpha/2)*pi/(n + alpha)), 1]`` for an even ``n``.

        ``C_n^(alpha)`` is the Jacobi polynomial with both parameters ``alpha - 0.5``, up to a constant factor.
        """
        return jacobi_interval_bounds(n, alpha - 0.5, alpha - 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that combines the degrees of `SWEPT_DEGREES` with ``alpha`` from -0.4 to 2 in steps of 0.2.

        - The sweep starts at -0.4, its lowest step above `ALPHA_LOWER_LIMIT`.
        - The sweep ends at 2, where the swings in the middle of ``[-1, 1]`` are already thousands of times lower
          than the value at the bounds for a degree above 100. A higher ``alpha`` continues that trend and gives no
          other kind of function.
        """
        alpha_values = ParamAxis("alpha", -0.4, 2.0, 0.2).values()
        return (degree_sweep_recipe(self.param_names, alpha_values),)

    def is_param_tuple_valid(self, n: float, alpha: float) -> bool:
        """Require ``n`` to be an integer of at least 1, and ``alpha`` to be in its valid range."""
        return is_valid_degree(n) and ALPHA_LOWER_LIMIT < alpha <= HIGHEST_ALPHA

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0, "alpha": 0.6}, x=0.3, c=0.0, expected=0.3),  # R_1(y) = y
        FormulaTestCase.value(params={"n": 2.0, "alpha": 0.0}, x=0.5, c=0.0, expected=-0.5),  # T_2(0.5)
        FormulaTestCase.value(params={"n": 2.0, "alpha": 0.0}, x=1.0, c=2.0, expected=-0.5),  # c shifts x to y = 0.5
        FormulaTestCase.value(params={"n": 3.0, "alpha": 0.5}, x=0.5, c=0.0, expected=-0.4375),  # Legendre's P_3(0.5)
        FormulaTestCase.value(params={"n": 2.0, "alpha": 1.0}, x=0.75, c=0.0, expected=1.25 / 3.0),  # U_2(0.75)/3
        FormulaTestCase.value(params={"n": 4.0, "alpha": -0.4}, x=1.0, c=0.0, expected=1.0),  # 1 at y = 1
        FormulaTestCase.invalid(params={"n": 2.5, "alpha": 0.6}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 2.0, "alpha": -0.5}),  # alpha at its lower limit
        FormulaTestCase.invalid(params={"n": 2.0, "alpha": 7.5}),  # alpha above the highest one
        FormulaTestCase.interval_bounds(params={"n": 3.0, "alpha": 1.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"n": 4.0, "alpha": 1.0}, expected=(-math.cos(0.3 * math.pi), 1.0)),
    )
