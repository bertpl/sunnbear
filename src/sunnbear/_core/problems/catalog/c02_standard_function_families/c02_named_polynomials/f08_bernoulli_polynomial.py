"""This formula is the Bernoulli polynomial of an odd degree with ``x`` shifted by ``c``, ``B_n(x - c)``."""

import math
from fractions import Fraction

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamGrid, ParamRecipe

from .helpers import is_valid_degree

# The degrees in `DEGREE_RANGES_WITH_INTERVALS` must not exceed this one, because `BERNOULLI_NUMBERS` holds the
# Bernoulli numbers up to this index only. A higher degree adds real zeros only slowly, about 1 per 4 degrees.
HIGHEST_VALID_DEGREE = 49
# Each entry holds the lowest and the highest degree of a recipe, and the bounds ``a`` and ``b`` of the interval that
# the recipe gives to every odd degree between them.
DEGREE_RANGES_WITH_INTERVALS = (
    (1.0, 23.0, -1.5, 2.5),
    (25.0, 39.0, -2.5, 3.5),
    (41.0, 49.0, -3.5, 4.5),
)


class BernoulliPolynomial(Formula):
    """`BernoulliPolynomial` is ``B_n(x - c)`` on ``[a, b]``, with ``B_n`` the Bernoulli polynomial of an odd degree.

    Between its outermost real zeros, ``B_n`` is close to a sine whose zeros lie 0.5 apart and whose amplitude is the
    same everywhere. Beyond those zeros it grows as ``x^n``.

    - ``n`` is the degree, an odd integer from 1 to `HIGHEST_VALID_DEGREE`.
    - ``a`` and ``b`` are the bounds of the interval, which lie equally far from 0.5, so that ``a + b = 1``.

    The interval is a parameter because no closed-form expression gives it: most zeros of ``B_n`` are complex, and
    the number of real zeros does not grow steadily with ``n``, so the largest real zero does not either.

    Each recipe therefore gives 1 interval to a range of degrees, and the interval is wide enough to hold every real
    zero of each degree in that range.

    Only an odd ``n`` is valid. ``B_n(1 - x) = (-1)^n * B_n(x)``, so on an interval around 0.5 an odd degree has
    opposite signs at the 2 bounds, while an even degree has the same sign at both.

    ``c`` shifts ``x`` by ``c`` itself, not by ``c/n^2`` as in the formulas whose polynomials are orthogonal on
    ``[-1, 1]``, because the zeros lie 0.5 apart for every ``n``.

    References:
        - NIST Digital Library of Mathematical Functions, §24.2(i), for the definition. https://dlmf.nist.gov/24.2
        - NIST Digital Library of Mathematical Functions, §24.4(i) and §24.4(ii), for the difference equation and the
          symmetry. https://dlmf.nist.gov/24.4
        - NIST Digital Library of Mathematical Functions, §24.12(i), for the real zeros. https://dlmf.nist.gov/24.12
    """

    number = (2, 2, 8)
    name = "Bernoulli polynomial"
    param_names = ("n", "a", "b")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, a: float, b: float) -> float:
        """Evaluate ``B_n(x - c)`` from the polynomial's values on ``[0, 1)``.

        Evaluating ``B_n(y) = sum over k = 0..n of binomial(n, k)*B_k*y^(n-k)`` at ``y`` itself loses accuracy near
        the zeros as ``n`` and ``abs(y)`` grow, because its terms cancel.

        The terms cancel far less on ``[0, 1)``, so the function evaluates the sum only there, and reaches every other
        ``y`` through 2 identities: a reflection about 0.5, and steps of 1 along x.
        """
        degree = int(n)
        y = x - c
        # B_n(1 - y) = -B_n(y) for an odd n, which maps a y below 0.5 to one above it.
        if y < 0.5:
            y = 1.0 - y
            sign = -1.0
        else:
            sign = 1.0
        # y is at least 0.5 here, so int(y) is its whole part.
        n_whole_steps = int(y)
        t = y - n_whole_steps
        # Horner's rule evaluates the sum at t, which lies in [0, 1).
        value = 0.0
        binomial = 1.0
        for k in range(degree + 1):
            value = value * t + binomial * BERNOULLI_NUMBERS[k]
            binomial = binomial * (degree - k) / (k + 1)
        # B_n(z + 1) = B_n(z) + n*z^(n-1) takes the value from t to y, 1 whole step at a time.
        for step in range(n_whole_steps):
            value += degree * (t + step) ** (degree - 1)
        return sign * value

    def interval_bounds(self, n: float, a: float, b: float) -> tuple[float, float]:
        """Return the interval ``[a, b]``, which the parameters give."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 1 recipe per entry of `DEGREE_RANGES_WITH_INTERVALS`: its odd degrees, on its interval.

        Each interval has half-integer bounds, and in every candidate the largest real zero lies at least 0.25 inside
        the upper bound. `[-1.5, 2.5]` would lose that margin at degree 25, and `[-2.5, 3.5]` at degree 41, which is
        where the next interval takes over.
        """
        return tuple(
            ParamGrid(
                axes=(
                    ParamAxis("n", lowest_degree, highest_degree, 2.0),
                    ParamAxis("a", a, a, 1.0),
                    ParamAxis("b", b, b, 1.0),
                )
            )
            for lowest_degree, highest_degree, a, b in DEGREE_RANGES_WITH_INTERVALS
        )

    def is_param_tuple_valid(self, n: float, a: float, b: float) -> bool:
        """Require an odd integer ``n`` of at most `HIGHEST_VALID_DEGREE`, and ``a < 0.5 < b`` with ``a + b = 1``."""
        if not is_valid_degree(n) or n > HIGHEST_VALID_DEGREE or int(n) % 2 == 0:
            return False
        else:
            return a < 0.5 < b and a + b == 1.0

    test_cases = (
        # B_1(y) = y - 0.5
        FormulaTestCase.value(params={"n": 1.0, "a": -1.5, "b": 2.5}, x=0.75, c=0.0, expected=0.25),
        # B_3(y) = y^3 - 1.5*y^2 + 0.5*y
        FormulaTestCase.value(params={"n": 3.0, "a": -1.5, "b": 2.5}, x=0.75, c=0.0, expected=-0.046875),
        # c shifts x to y = 0.75
        FormulaTestCase.value(params={"n": 3.0, "a": -1.5, "b": 2.5}, x=1.0, c=0.25, expected=-0.046875),
        # 2 whole steps above [0, 1): B_3(2.5) = 15.625 - 9.375 + 1.25
        FormulaTestCase.value(params={"n": 3.0, "a": -1.5, "b": 2.5}, x=2.5, c=0.0, expected=7.5),
        # below 0.5: B_3(-1.5) = -B_3(2.5)
        FormulaTestCase.value(params={"n": 3.0, "a": -1.5, "b": 2.5}, x=-1.5, c=0.0, expected=-7.5),
        FormulaTestCase.invalid(params={"n": 2.5, "a": -1.5, "b": 2.5}),  # degree that is not an integer
        FormulaTestCase.invalid(params={"n": 4.0, "a": -1.5, "b": 2.5}),  # even degree
        FormulaTestCase.invalid(params={"n": 51.0, "a": -3.5, "b": 4.5}),  # degree above the highest one
        FormulaTestCase.invalid(params={"n": 3.0, "a": -1.5, "b": 3.0}),  # interval that is not centered on 0.5
        FormulaTestCase.interval_bounds(params={"n": 3.0, "a": -1.5, "b": 2.5}, expected=(-1.5, 2.5)),
    )


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _compute_bernoulli_numbers(highest_index: int) -> tuple[float, ...]:
    """Return the Bernoulli numbers ``B_0`` to ``B_highest_index``, with ``B_1 = -1/2``.

    The numbers follow in exact arithmetic from ``sum over k = 0..m of binomial(m + 1, k)*B_k = 0`` for every ``m`` of
    at least 1, and are rounded to floats at the end.
    """
    numbers = [Fraction(1)]
    for m in range(1, highest_index + 1):
        sum_of_lower_terms = sum((math.comb(m + 1, k) * numbers[k] for k in range(m)), start=Fraction(0))
        numbers.append(-sum_of_lower_terms / (m + 1))
    return tuple(float(number) for number in numbers)


# `BernoulliPolynomial.parametrized_fun` reads this table as a global, because numba compiles that function without
# its class.
BERNOULLI_NUMBERS = _compute_bernoulli_numbers(HIGHEST_VALID_DEGREE)
