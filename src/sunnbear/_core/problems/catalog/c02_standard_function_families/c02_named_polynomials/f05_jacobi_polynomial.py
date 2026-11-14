"""This formula is the Jacobi polynomial, divided by its value at 1, with ``x`` shifted by ``c``."""

import itertools

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamRecipe, ParamTable

from .helpers import SWEPT_DEGREES, is_valid_degree, jacobi_interval_bounds

# ``alpha`` and ``beta`` have to be above this value: the Jacobi polynomials are orthogonal on ``[-1, 1]`` only above
# it.
ALPHA_BETA_EXCLUSIVE_LOWER_LIMIT = -1.0
# Up to this value of ``alpha`` and ``beta``, the tests check that the lower bound from `jacobi_interval_bounds` lies
# between the 2 lowest zeros.
ALPHA_BETA_INCLUSIVE_UPPER_LIMIT = 3.0


class JacobiPolynomial(Formula):
    """`JacobiPolynomial` is ``P_n^(alpha, beta)(y)/P_n^(alpha, beta)(1)`` at ``y = x - c/n^2``.

    ``P_n^(alpha, beta)`` is the Jacobi polynomial.

    - ``n`` is the degree, an integer of at least 1. The function has ``n`` zeros in its interval for an odd ``n``,
      and ``n - 1`` for an even ``n``.
    - ``alpha`` sets how the amplitude changes toward the bound 1, and ``beta`` how it changes toward the bound -1.
      Toward the bound of a parameter, the amplitude:

      - grows, for a parameter value above -0.5;
      - stays the same, at -0.5;
      - shrinks, for a parameter value below -0.5.

      ``alpha`` and ``beta`` each lie above `ALPHA_BETA_EXCLUSIVE_LOWER_LIMIT` and are at most
      `ALPHA_BETA_INCLUSIVE_UPPER_LIMIT`.

    With ``alpha`` unequal to ``beta``, the function behaves differently at its 2 ends, which no other formula of the
    category does. With ``alpha`` equal to ``beta`` it is the function of `GegenbauerPolynomial`, whose ``alpha`` is
    0.5 higher.

    The pairs ``(-0.5, 0.5)`` and ``(0.5, -0.5)`` give the Chebyshev polynomials of the third and the fourth kind, up
    to a constant factor.

    The polynomial is divided by its value at 1, so that the function is 1 at ``y = 1`` for every parameter tuple, as
    the function of `GegenbauerPolynomial` is. The division moves no zero, because it only scales the function.

    References:
        - NIST Digital Library of Mathematical Functions, §18.3, for the definition and for the Chebyshev polynomials
          of the third and the fourth kind. https://dlmf.nist.gov/18.3
        - NIST Digital Library of Mathematical Functions, §18.6(i), for the value at 1. https://dlmf.nist.gov/18.6
        - NIST Digital Library of Mathematical Functions, §18.9(i), for the recurrence. https://dlmf.nist.gov/18.9
    """

    number = (2, 2, 5)
    name = "Jacobi polynomial"
    param_names = ("n", "alpha", "beta")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, alpha: float, beta: float) -> float:
        """Evaluate ``R_n(x - c/n^2)``, with ``R_k(y) = P_k^(alpha, beta)(y)/P_k^(alpha, beta)(1)``.

        With ``s = alpha + beta`` and ``t = 2*k + s``, the recurrence is
        ``2*(k + s)*(t - 2)*(k + alpha)*R_k(y) = (t - 1)*(t*(t - 2)*y + alpha^2 - beta^2)*R_(k-1)(y)
        - 2*(k - 1)*(k + beta - 1)*t*R_(k-2)(y)``, which follows from the recurrence of ``P_k^(alpha, beta)`` and its
        value at 1. The recurrence takes ``n`` steps and holds for every ``x``.
        """
        y = x - c / (n * n)
        s = alpha + beta
        r_previous = 1.0
        r = 1.0 + (s + 2.0) * (y - 1.0) / (2.0 * (alpha + 1.0))
        for k in range(2, int(n) + 1):
            t = 2.0 * k + s
            r_previous, r = (
                r,
                (
                    (t - 1.0) * (t * (t - 2.0) * y + alpha * alpha - beta * beta) * r
                    - 2.0 * (k - 1.0) * (k + beta - 1.0) * t * r_previous
                )
                / (2.0 * (k + s) * (t - 2.0) * (k + alpha)),
            )
        return r

    def interval_bounds(self, n: float, alpha: float, beta: float) -> tuple[float, float]:
        """Return ``[-1, 1]`` for an odd ``n``, and the interval that leaves out the lowest zero for an even ``n``."""
        return jacobi_interval_bounds(n, alpha, beta)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that combines the degrees of `SWEPT_DEGREES` with 6 values of ``alpha`` and of ``beta``.

        Both parameters take -0.75 and the values from -0.5 to 1.5 in steps of 0.5:

        - The value -0.75 is the only one at which the amplitude shrinks toward a bound. It lies midway between
          `ALPHA_BETA_EXCLUSIVE_LOWER_LIMIT` and -0.5, the value at which the amplitude stays the same.
        - The values end at 1.5, because the recipe of `GegenbauerPolynomial` ends at an ``alpha`` of 2, and that
          formula's ``alpha`` is 0.5 higher than the ``alpha`` and ``beta`` here.
        """
        alpha_beta_values = (-0.75, *ParamAxis("alpha", -0.5, 1.5, 0.5).values())
        rows = tuple(itertools.product(SWEPT_DEGREES, alpha_beta_values, alpha_beta_values))
        return (ParamTable(names=self.param_names, rows=rows),)

    def is_param_tuple_valid(self, n: float, alpha: float, beta: float) -> bool:
        """Require ``n`` to be an integer of at least 1, and ``alpha`` and ``beta`` to be in their valid range."""
        if not is_valid_degree(n):
            return False
        else:
            return (
                ALPHA_BETA_EXCLUSIVE_LOWER_LIMIT < alpha <= ALPHA_BETA_INCLUSIVE_UPPER_LIMIT
                and ALPHA_BETA_EXCLUSIVE_LOWER_LIMIT < beta <= ALPHA_BETA_INCLUSIVE_UPPER_LIMIT
            )

    test_cases = (
        # R_1(y) = 1 + (alpha + beta + 2)*(y - 1)/(2*(alpha + 1)) = 1 - 3/4
        FormulaTestCase.value(params={"n": 1.0, "alpha": 1.0, "beta": 0.0}, x=0.0, c=0.0, expected=0.25),
        # Legendre's P_2(0.5)
        FormulaTestCase.value(params={"n": 2.0, "alpha": 0.0, "beta": 0.0}, x=0.5, c=0.0, expected=-0.125),
        # c shifts x by c/4, to y = 0.5
        FormulaTestCase.value(params={"n": 2.0, "alpha": 0.0, "beta": 0.0}, x=1.0, c=2.0, expected=-0.125),
        # U_2(0.75)/3, with U_2 the Chebyshev polynomial of the second kind
        FormulaTestCase.value(params={"n": 2.0, "alpha": 0.5, "beta": 0.5}, x=0.75, c=0.0, expected=1.25 / 3.0),
        # the Chebyshev polynomial of the third kind: cos(2.5*t)/cos(0.5*t) at t = acos(0.5) = pi/3
        FormulaTestCase.value(params={"n": 2.0, "alpha": -0.5, "beta": 0.5}, x=0.5, c=0.0, expected=-1.0),
        FormulaTestCase.invalid(params={"n": 0.0, "alpha": 0.0, "beta": 0.0}),  # degree below 1
        FormulaTestCase.invalid(params={"n": 2.0, "alpha": -1.0, "beta": 0.0}),  # alpha at its lower limit
        FormulaTestCase.invalid(params={"n": 2.0, "alpha": 0.0, "beta": 3.5}),  # beta above the highest value
        FormulaTestCase.interval_bounds(params={"n": 3.0, "alpha": -0.5, "beta": 0.5}, expected=(-1.0, 1.0)),
        # -cos(theta) with theta = (1.25 + 0.25)*pi/(4 + 0.5) = pi/3
        FormulaTestCase.interval_bounds(params={"n": 4.0, "alpha": -0.5, "beta": 0.5}, expected=(-0.5, 1.0)),
    )
