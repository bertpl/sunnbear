"""This formula is a line plus the mean ``E_n(x)`` of ``n`` even powers from 2, ``x + w*(E_n(x) - 1) + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_term_count, term_count_axis, weight_recipes

# ``LOWEST_POWER`` is the lowest power of the sum.
LOWEST_POWER = 2


class LinearPlusSumOfEvenPowers(Formula):
    """`LinearPlusSumOfEvenPowers` is the polynomial ``x + w*(E_n(x) - 1) + c`` with a sum of ``n`` even powers.

    ``E_n(x) = (x^2 + x^4 + ... + x^(2*n))/n`` is the mean of the first ``n`` even powers. Dividing by ``n`` makes the
    function pass through ``(-1, -1)`` and ``(1, 1)`` at ``c = 0``, for every ``n`` and ``w``.

    - ``n`` is the number of terms of the sum, at least 2: with 1 term the function equals the function of
      `LinearPlusEvenPower` at the power 2. More terms steepen the function toward the bounds. The term ``x^2`` keeps
      the function curved around 0 for every ``n``, whereas a single high power is nearly flat there.
    - ``w`` is the weight of the sum, as in `LinearPlusEvenPower`.
    """

    number = (2, 1, 4)
    name = "Linear plus sum of even powers"
    param_names = ("n", "w")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, w: float) -> float:
        """Evaluate ``x + w*(E_n(x) - 1) + c``."""
        n_terms = int(n)
        x_squared = x * x
        term = 1.0
        sum_of_powers = 0.0
        for _ in range(n_terms):
            term *= x_squared
            sum_of_powers += term
        return x + w * (sum_of_powers / n_terms - 1.0) + c

    def interval_bounds(self, n: float, w: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every number of terms with every weight."""
        return weight_recipes(term_count_axis(LOWEST_POWER))

    def is_param_tuple_valid(self, n: float, w: float) -> bool:
        """Require ``n`` to be an integer of at least 2."""
        return is_valid_term_count(n)

    test_cases = (
        # E_2(0.5) = (0.25 + 0.0625)/2 = 0.15625
        FormulaTestCase.value(params={"n": 2.0, "w": 1.0}, x=0.5, c=0.0, expected=-0.34375),
        FormulaTestCase.value(params={"n": 2.0, "w": 1.0}, x=0.5, c=0.5, expected=0.15625),  # c shifts the value
        FormulaTestCase.value(params={"n": 3.0, "w": 2.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"n": 2.5, "w": 1.0}),  # number of terms that is not an integer
        FormulaTestCase.invalid(params={"n": 1.0, "w": 1.0}),  # a sum of 1 term
        FormulaTestCase.interval_bounds(params={"n": 2.0, "w": 1.0}, expected=(-1.0, 1.0)),
    )
