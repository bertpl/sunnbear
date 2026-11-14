"""This formula is a line plus the mean ``O_n(x)`` of ``n`` odd powers from 3, ``m*x + (1 - m)*O_n(x) + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_term_count, slope_recipes, term_count_axis

# ``LOWEST_POWER`` is the lowest power of the sum.
LOWEST_POWER = 3


class LinearPlusSumOfOddPowers(Formula):
    """`LinearPlusSumOfOddPowers` is the polynomial ``m*x + (1 - m)*O_n(x) + c`` with a sum of ``n`` odd powers.

    ``O_n(x) = (x^3 + x^5 + ... + x^(2*n + 1))/n`` is the mean of the first ``n`` odd powers from 3. Dividing by ``n``
    makes the function pass through ``(-1, -1)`` and ``(1, 1)`` at ``c = 0``, for every ``n`` and ``m``.

    - ``n`` is the number of terms of the sum, at least 2: with 1 term the function equals the function of
      `LinearPlusOddPower` at the power 3. More terms steepen the function toward the bounds. The term ``x^3``
      dominates around 0 for every ``n``, whereas a single high power is much flatter there.
    - ``m`` is the slope at ``x = 0``, as in `LinearPlusOddPower`.
    """

    number = (2, 1, 5)
    name = "Linear plus sum of odd powers"
    param_names = ("n", "m")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, m: float) -> float:
        """Evaluate ``m*x + (1 - m)*O_n(x) + c``."""
        n_terms = int(n)
        x_squared = x * x
        term = x
        sum_of_powers = 0.0
        for _ in range(n_terms):
            term *= x_squared
            sum_of_powers += term
        return m * x + (1.0 - m) * sum_of_powers / n_terms + c

    def interval_bounds(self, n: float, m: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every number of terms with every slope."""
        return slope_recipes(term_count_axis(LOWEST_POWER))

    def is_param_tuple_valid(self, n: float, m: float) -> bool:
        """Require ``n`` to be an integer of at least 2."""
        return is_valid_term_count(n)

    test_cases = (
        # O_2(0.5) = (0.125 + 0.03125)/2 = 0.078125
        FormulaTestCase.value(params={"n": 2.0, "m": 0.5}, x=0.5, c=0.0, expected=0.2890625),
        FormulaTestCase.value(params={"n": 2.0, "m": 0.5}, x=0.5, c=0.25, expected=0.5390625),  # c shifts the value
        FormulaTestCase.value(params={"n": 3.0, "m": 0.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"n": 2.5, "m": 0.5}),  # number of terms that is not an integer
        FormulaTestCase.invalid(params={"n": 1.0, "m": 0.5}),  # a sum of 1 term
        FormulaTestCase.interval_bounds(params={"n": 2.0, "m": 0.5}, expected=(-1.0, 1.0)),
    )
